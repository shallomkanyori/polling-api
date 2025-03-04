from rest_framework import permissions, viewsets
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Poll
from .serializers import UserSerializer, PollSerializer
from .permissions import IsPollCreatorOrAdmin, IsSelfOrAdmin
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser

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

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsPollCreatorOrAdmin]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]