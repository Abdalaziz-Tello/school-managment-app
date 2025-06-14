import os
import requests
from typing import Optional

class SMSGateway:
    def __init__(self):
        self.api_key = os.getenv("SMS_API_KEY", "demo-key")
        self.base_url = "https://sms-gateway-demo.com/api/v1/send"  # Replace with actual SMS gateway URL

    def send_sms(self, phone_number: str, message: str) -> bool:
        """
        Send SMS using a generic SMS gateway.
        Returns True if successful, False otherwise.
        """
        try:
            response = requests.post(
                self.base_url,
                json={
                    "api_key": self.api_key,
                    "phone": phone_number,
                    "message": message
                },
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Error sending SMS: {str(e)}")
            return False

    def send_credentials(self, phone_number: str, username: str, password: str) -> bool:
        """
        Send login credentials via SMS.
        """
        message = f"Your school system credentials:\nUsername: {username}\nPassword: {password}\nPlease change your password after first login."
        return self.send_sms(phone_number, message)

# Create a singleton instance
sms_gateway = SMSGateway() 