from rest_framework import permissions, viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from .models import Poll, Option, Vote
from .serializers import UserSerializer, PollSerializer, VoteSerializer, PollResultsSerializer
from .permissions import IsPollCreatorOrAdmin, IsSelfOrAdmin
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from .utils import get_ip_hash
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django_filters.rest_framework import DjangoFilterBackend
from .filters import PollFilter
from rest_framework.throttling import ScopedRateThrottle
from .throttles import AdminThrottle, PollCreationThrottle, SignupThrottle
from django.utils.decorators import method_decorator
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoints for Users CRUD
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = [IsAuthenticated, IsAdminUser]
        elif self.action == 'create':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated, IsSelfOrAdmin]
        return [permission() for permission in permission_classes]
    
    def create(self, request, *args, **kwargs):
        self.throttle_classes = [SignupThrottle]
        return super().create(request, *args, **kwargs)

@method_decorator(name='list', decorator=swagger_auto_schema(
    manual_parameters=[
        openapi.Parameter(
            'title',
            openapi.IN_QUERY,
            description='Filter by title',
            type=openapi.TYPE_STRING
        ),
        openapi.Parameter(
            'created_by',
            openapi.IN_QUERY,
            description='Filter by creator ID',
            type=openapi.TYPE_INTEGER
        ),
        openapi.Parameter(
            'is_ongoing',
            openapi.IN_QUERY,
            description='Filter ongoing polls',
            type=openapi.TYPE_BOOLEAN
        ),
        ]
    )
)
class PollViewSet(viewsets.ModelViewSet):
    """
    API endpoints for Polls CRUD
    """
    queryset = Poll.objects.prefetch_related('options').all()
    serializer_class = PollSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = PollFilter

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsPollCreatorOrAdmin]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]
    
    def create(self, request, *args, **kwargs):
        self.throttle_classes = [PollCreationThrottle]
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(
        method='post',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['option'],
            properties={
                'option': openapi.Schema(type=openapi.TYPE_INTEGER, description='Option ID to vote for'),
            }
        )
    )
    @action(detail=True, methods=['POST'])
    def vote(self, request, pk=None):
        """
        API endpoint for voting in a poll
        """
        self.throttle_classes = [ScopedRateThrottle, AdminThrottle]
        self.throttle_scope = 'vote'

        poll = get_object_or_404(Poll, pk=pk)

        user = request.user
        if not user or not user.is_authenticated or user.is_anonymous:
            user = None
            request.data['ip_hash'] = get_ip_hash(request.META['REMOTE_ADDR'])
            
            session_id = request.session.session_key
            if not session_id:
                request.session.create()
                session_id = request.session.session_key
            request.data['session_id'] = session_id
        
        serializer = VoteSerializer(data=request.data, context={'poll': poll, 'user': user})
        if serializer.is_valid():
            serializer.save(poll=poll)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        method='get',
        responses={200: PollResultsSerializer}
    )
    @action(detail=True, methods=['GET'])
    def results(self, request, pk=None):
        """
        API endpoint for viewing poll results
        """
        poll = get_object_or_404(Poll, pk=pk)
        serializer = PollResultsSerializer(poll)
        return Response(serializer.data)

# Auth Views

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom TokenObtainPairView to add swagger documentation
    """
    @swagger_auto_schema(
        tags=['auth'],
        operation_summary='Login',
        operation_description='Authenticate a user and get access & refresh tokens',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['username', 'password'],
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING),
                'password': openapi.Schema(type=openapi.TYPE_STRING),
            }
        )
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class CustomTokenRefreshView(TokenRefreshView):
    """
    Custom TokenRefreshView to add swagger documentation
    """
    @swagger_auto_schema(
        tags=['auth'],
        operation_summary='Refresh Token',
        operation_description='Get a new access token using the refresh token',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['refresh'],
            properties={
                'refresh': openapi.Schema(type=openapi.TYPE_STRING),
            }
        )
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

@swagger_auto_schema(
    method='post',
    tags=['auth'],
    operation_summary='Signup',
    operation_description='Create a new user account',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['username', 'email', 'password'],
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING),
            'email': openapi.Schema(type=openapi.TYPE_STRING),
            'password': openapi.Schema(type=openapi.TYPE_STRING),
        }
    )
)
@api_view(['POST'])
def signup(request):
    """
    API endpoint for user signup
    """
    userviewset = UserViewSet()
    return userviewset.create(request)

@swagger_auto_schema(
    method='post',
    tags=['auth'],
    operation_summary='Logout',
    operation_description='Logs out user by blacklisting the refresh token',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['refresh_token'],
        properties={
            'refresh_token': openapi.Schema(type=openapi.TYPE_STRING),
        }
    )
)
@api_view(['POST'])
def logout(request):
    """
    API endpoint for user logout
    """
    refresh_token = request.data.get('refresh_token')
    if not refresh_token:
        response = {'message': 'Refresh token is required'}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        token = RefreshToken(refresh_token)
        token.blacklist()

        response = {'message': 'You have successfully logged out'}
        return Response(response, status=status.HTTP_200_OK)
    except Exception as e:
        response = {'message': 'Invalid refresh token'}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='post',
    tags=['auth'],
    operation_summary='Forgot Password',
    operation_description='Send an email with a link to reset your password',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['email', 'front_end_url'],
        properties={
            'email': openapi.Schema(type=openapi.TYPE_STRING),
            'front_end_url': openapi.Schema(type=openapi.TYPE_STRING, description='Frontend URL where user will reset password'),
            'sender_email': openapi.Schema(type=openapi.TYPE_STRING, description='Email address to send the reset link from'),
        }
    )
)
@api_view(['POST'])
def forgot_password(request):
    """
    API endpoint for password reset
    """
    email = request.data.get('email')
    front_end_url = request.data.get('front_end_url')
    if not email:
        response = {'message': 'Email is required'}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)
    elif not front_end_url:
        response = {'message': 'Frontend URL is required'}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

    sender_email = request.data.get('sender_email', settings.DEFAULT_FROM_EMAIL)
    user = get_object_or_404(User, email=email)

    try:
        token = default_token_generator.make_token(user)

        send_mail(
            'Password Reset',
            f'Click the link to reset your password: {front_end_url}?token={token}&uid={user.id}',
            sender_email,
            [email],
            fail_silently=False,
        )

        response = {'message': 'Password reset email sent'}
        return Response(response, status=status.HTTP_200_OK)
    except Exception as e:
        response = {'message': 'An error occurred'}
        return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@swagger_auto_schema(
    method='post',
    tags=['auth'],
    operation_summary='Reset Password',
    operation_description='Reset user password using the token sent to their email',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['token', 'uid', 'password'],
        properties={
            'token': openapi.Schema(type=openapi.TYPE_STRING, description='Token sent to user email'),
            'uid': openapi.Schema(type=openapi.TYPE_INTEGER, description='User ID'),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description='New password'),
        }
    )
)
@api_view(['POST'])
def reset_password(request):
    """
    API endpoint for password reset
    """
    token = request.data.get('token')
    uid = request.data.get('uid')
    password = request.data.get('password')
    if not token:
        response = {'message': 'Token is required'}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)
    elif not uid:
        response = {'message': 'User ID is required'}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)
    elif not password:
        response = {'message': 'Password is required'}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

    user = get_object_or_404(User, pk=uid)
    try:
        if  not default_token_generator.check_token(user, token):
            response = {'message': 'Invalid or expired token'}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(password)
        user.save()

        response = {'message': 'Password reset successful'}
        return Response(response, status=status.HTTP_200_OK)
    except Exception as e:
        response = {'message': 'An error occurred'}
        return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)