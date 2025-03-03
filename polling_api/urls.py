from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, PollViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'polls', PollViewSet)

urlpatterns = [
    path('', include(router.urls)),
]