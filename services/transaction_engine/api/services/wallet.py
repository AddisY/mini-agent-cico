import logging
import requests
from decimal import Decimal
from django.conf import settings

logger = logging.getLogger(__name__)

class WalletServiceClient:
    """
    Client for interacting with the Wallet Service
    """
    
    def __init__(self):
        self.base_url = settings.WALLET_SERVICE_URL
        
    def check_balance(self, agent_id: str, amount: Decimal, auth_token: str) -> tuple[bool, str]:
        """
        Check if an agent has sufficient balance for a transaction
        Returns: (has_sufficient_balance, error_message)
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/wallets/balance/",
                headers={
                    "Authorization": auth_token
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                current_balance = Decimal(data['balance'])
                has_sufficient_balance = current_balance >= amount
                
                if has_sufficient_balance:
                    return True, None
                else:
                    return False, f"Insufficient balance. Required: {amount}, Available: {current_balance}"
            elif response.status_code == 404:
                return False, "Wallet not found"
            else:
                logger.error(f"Wallet service error: {response.text}")
                return False, "Error checking wallet balance"
                
        except Exception as e:
            logger.error(f"Error calling wallet service: {str(e)}")
            return False, "Error connecting to wallet service" 