from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

class AdminThrottle(UserRateThrottle):
    scope = 'admin'
    
    def allow_request(self, request, view):
        if request.user.is_authenticated and request.user.is_staff:
            self.scope = 'admin'
        else:
            self.scope = 'user'
        return super().allow_request(request, view)

class PollCreationThrottle(UserRateThrottle):
    scope = 'poll_creation'

class SignupThrottle(AnonRateThrottle):
    scope = 'signup'