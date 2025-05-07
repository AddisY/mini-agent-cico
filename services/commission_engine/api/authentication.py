import requests
from django.conf import settings
from rest_framework import authentication
from rest_framework import exceptions

class UserManagementAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        # Get the token from the request header
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header:
            return None

        try:
            # Verify token with user management service
            response = requests.get(
                f"{settings.USER_SERVICE_URL}/api/v1/auth/verify/",
                headers={'Authorization': auth_header}
            )
            
            if response.status_code == 200:
                user_data = response.json()
                return (user_data, None)
            else:
                raise exceptions.AuthenticationFailed('Invalid token')
                
        except requests.RequestException:
            raise exceptions.AuthenticationFailed('User service unavailable') 