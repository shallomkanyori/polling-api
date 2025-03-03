from rest_framework import permissions, viewsets
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Poll
from .serializers import UserSerializer, PollSerializer
from .permissions import IsPollCreatorOrAdmin
from rest_framework.permissions import IsAuthenticated, AllowAny

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoints for Users CRUD
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

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