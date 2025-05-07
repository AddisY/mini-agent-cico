import requests
import logging
from django.conf import settings
from rest_framework import authentication
from rest_framework import exceptions

logger = logging.getLogger(__name__)

class CustomUser:
    def __init__(self, user_data):
        self.user_data = user_data
        self.is_authenticated = True
        
    def __getattr__(self, name):
        return self.user_data.get(name)

class UserManagementTokenAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        # Get the token from the request header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        logger.info(f"Auth header received: {auth_header}")
        
        if not auth_header:
            return None

        try:
            # Check if it starts with 'Bearer '
            auth_parts = auth_header.split()
            if auth_parts[0].lower() != 'bearer':
                return None
            if len(auth_parts) != 2:
                raise exceptions.AuthenticationFailed('Invalid token header')
            token = auth_parts[1]
            logger.info(f"Token extracted: {token[:10]}...")  # Log first 10 chars of token
        except IndexError:
            raise exceptions.AuthenticationFailed('Invalid token format')

        # Get user details using the token
        user_url = f"{settings.USER_MANAGEMENT_SERVICE_URL}/api/users/me/"
        logger.info(f"Fetching user details from: {user_url}")
        
        try:
            user_response = requests.get(
                user_url,
                headers={'Authorization': f'Bearer {token}'}
            )
            logger.info(f"User details response status: {user_response.status_code}")
            logger.info(f"User details response: {user_response.text}")
            
            if user_response.status_code == 200:
                user_data = user_response.json()
                logger.info(f"Full user data received: {user_data}")
                logger.info(f"User role: {user_data.get('role')}")
                logger.info(f"Agent profile data: {user_data.get('agent_profile')}")
                
                # Check if the user is an agent
                if user_data.get('role') != 'AGENT':
                    raise exceptions.AuthenticationFailed('Only agents can perform transactions')
                
                # Get agent_id from agent_profile
                agent_profile = user_data.get('agent_profile')
                if not agent_profile or not agent_profile.get('agent_id'):
                    logger.error(f"Agent profile not found or missing agent_id. User data: {user_data}")
                    raise exceptions.AuthenticationFailed('Agent ID not found in user profile')
                
                # Create a CustomUser instance with the agent_id
                user_data['agent_id'] = agent_profile['agent_id']
                user = CustomUser(user_data)
                return (user, token)
            else:
                raise exceptions.AuthenticationFailed('Invalid token or user not found')
                
        except requests.RequestException as e:
            logger.error(f"Request exception during authentication: {str(e)}")
            raise exceptions.AuthenticationFailed(f'Could not authenticate with user management service: {str(e)}') 