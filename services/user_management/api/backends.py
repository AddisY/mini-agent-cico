from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
import logging

logger = logging.getLogger(__name__)

class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, email=None, **kwargs):
        UserModel = get_user_model()
        try:
            # Try to fetch the user by email (either from email or username field)
            email_to_use = email or username
            logger.info(f"Attempting to authenticate user with email: {email_to_use}")
            
            user = UserModel.objects.get(email=email_to_use)
            if user.check_password(password):
                logger.info(f"Authentication successful for user: {email_to_use}")
                return user
            else:
                logger.warning(f"Password check failed for user: {email_to_use}")
                return None
        except UserModel.DoesNotExist:
            logger.warning(f"No user found with email: {email_to_use}")
            return None

    def get_user(self, user_id):
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None 