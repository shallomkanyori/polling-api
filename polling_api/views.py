from rest_framework import permissions, viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
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
    
    @swagger_auto_schema(
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
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
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