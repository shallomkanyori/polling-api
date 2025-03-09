from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, PollViewSet, CustomTokenObtainPairView, CustomTokenRefreshView, signup, logout, forgot_password, reset_password


router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'polls', PollViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/signup/', signup, name='signup'),
    path('auth/logout/', logout, name='logout'),
    path('auth/forgot-password/', forgot_password, name='forgot_password'),
    path('auth/reset-password/', reset_password, name='reset_password'),
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
]