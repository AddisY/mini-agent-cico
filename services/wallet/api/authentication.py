import logging
import requests
from django.conf import settings
from rest_framework import authentication, exceptions
from rest_framework.request import Request

logger = logging.getLogger(__name__)

class UserManagementAuthentication(authentication.BaseAuthentication):
    """
    Custom authentication class that validates JWT tokens with the User Management Service
    """
    
    def authenticate(self, request: Request):
        """
        Authenticate the request by validating the JWT token with the User Management Service
        """
        # Get the Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header:
            return None

        try:
            # Check if it starts with 'Bearer '
            auth_parts = auth_header.split()
            if auth_parts[0].lower() != 'bearer' or len(auth_parts) != 2:
                raise exceptions.AuthenticationFailed('Invalid token header')
            
            token = auth_parts[1]
            
            # Validate token with User Management Service
            response = requests.get(
                f"{settings.USER_SERVICE_URL}/api/users/me/",
                headers={'Authorization': f'Bearer {token}'}
            )
            
            if response.status_code == 200:
                user_data = response.json()
                # Create a simple user object with required attributes
                user = type('User', (), {
                    'id': user_data['id'],
                    'is_authenticated': True,
                    'is_active': user_data.get('is_active', True),
                    'is_staff': user_data.get('is_staff', False),
                    'is_superuser': user_data.get('is_superuser', False),
                })()

                # Get agent_id from agent_profile
                agent_profile = user_data.get('agent_profile', {})
                if not agent_profile or not agent_profile.get('agent_id'):
                    logger.error(f"Agent profile not found or missing agent_id. User data: {user_data}")
                    raise exceptions.AuthenticationFailed('Agent ID not found in user profile')

                # Create an auth object that includes agent_id
                auth = type('Auth', (), {
                    'agent_id': agent_profile['agent_id'],
                    'token': token
                })()

                return (user, auth)
            else:
                logger.error(f"Token validation failed: {response.status_code} - {response.text}")
                raise exceptions.AuthenticationFailed('Invalid token')
                
        except requests.RequestException as e:
            logger.error(f"Error validating token with User Management Service: {str(e)}")
            raise exceptions.AuthenticationFailed('Error validating token')
        except Exception as e:
            logger.error(f"Unexpected error in authentication: {str(e)}")
            raise exceptions.AuthenticationFailed('Authentication failed') 