# sms_utils.py
import requests
import json
from urllib.parse import quote
import logging

logger = logging.getLogger(__name__)


class SMSAPI:
    def __init__(self):
        self.username = 'AUTHYD1'
        self.api_key = '333e1783fe5aae5fd76d'
        self.base_url = 'https://smslogin.co/v3/api.php'
        self.sender_id = 'AUTHYD'

        # ✅ CORRECT TEMPLATE ID FROM YOUR LOGS
        self.template_id = '1707177468286303768'

    # ---------------------------------------------------------
    # ✅ DLT MESSAGE VALIDATION
    # ---------------------------------------------------------
    def validate_dlt_message(self, message):
        """
        Basic validation for DLT template compliance
        """
        required_parts = [
            "Fee due of Rs",
            "month(s)",
            "Adm No:",
            "Ignore if paid",
            "Idara Ashraful Uloom"
        ]
        
        for part in required_parts:
            if part not in message:
                return False, f"Invalid template: missing '{part}'"
        
        return True, None

    # ---------------------------------------------------------
    # ✅ SEND SMS
    # ---------------------------------------------------------
    def send_sms(self, mobile_numbers, message, template_id=None):
        try:
            if template_id is None:
                template_id = self.template_id

            # Validate message
            is_valid, error = self.validate_dlt_message(message)
            if not is_valid:
                logger.error(f"DLT Validation Failed: {error}")
                return {
                    'success': False,
                    'error': error,
                    'message': message
                }

            # Clean mobile numbers
            if isinstance(mobile_numbers, list):
                clean_numbers = []
                for num in mobile_numbers:
                    clean_num = ''.join(filter(str.isdigit, str(num)))
                    if len(clean_num) >= 10:
                        clean_numbers.append(clean_num)
                
                if not clean_numbers:
                    return {
                        'success': False,
                        'error': 'No valid mobile numbers'
                    }
                mobile = ','.join(clean_numbers)
            else:
                mobile = ''.join(filter(str.isdigit, str(mobile_numbers)))
                if len(mobile) < 10:
                    return {
                        'success': False,
                        'error': f'Invalid mobile number: {mobile_numbers}'
                    }

            # Encode message
            encoded_message = quote(message)

            # Build URL
            url = (
                f"{self.base_url}"
                f"?username={self.username}"
                f"&apikey={self.api_key}"
                f"&senderid={self.sender_id}"
                f"&mobile={mobile}"
                f"&message={encoded_message}"
                f"&templateid={template_id}"
            )

            logger.info(f"Sending SMS to: {mobile}")
            logger.info(f"Message: {message}")
            logger.info(f"Template ID: {template_id}")

            # Send request
            response = requests.get(url, timeout=30)

            logger.info(f"Response Code: {response.status_code}")
            logger.info(f"Response Text: {response.text}")

            # Handle response
            if response.status_code == 200:
                response_text = response.text.strip()
                
                if 'TEMPLATE_ERROR' in response_text:
                    return {
                        'success': False,
                        'error': 'Template ID mismatch or not approved',
                        'response': response_text
                    }
                
                if 'error' in response_text.lower():
                    return {
                        'success': False,
                        'error': response_text,
                        'response': response_text
                    }

                return {
                    'success': True,
                    'message_id': response_text,
                    'response': response_text,
                    'mobile': mobile,
                    'template_id': template_id
                }
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}",
                    'response': response.text
                }

        except requests.exceptions.Timeout:
            return {'success': False, 'error': 'Request timed out'}
        except requests.exceptions.ConnectionError:
            return {'success': False, 'error': 'Connection error'}
        except Exception as e:
            logger.exception("SMS sending error")
            return {'success': False, 'error': str(e)}

    # ---------------------------------------------------------
    # ✅ CHECK BALANCE
    # ---------------------------------------------------------
    def check_balance(self):
        try:
            url = f"{self.base_url}?username={self.username}&apikey={self.api_key}"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                response_text = response.text.strip()
                
                # Try to extract credits
                try:
                    credits = int(response_text)
                    return {'success': True, 'credits': credits}
                except:
                    pass
                
                try:
                    data = json.loads(response_text)
                    credits = data.get('Credits') or data.get('credits') or data.get('balance')
                    if credits:
                        return {'success': True, 'credits': credits}
                except:
                    pass

                return {
                    'success': True,
                    'credits': response_text,
                    'raw': response_text
                }

            return {'success': False, 'error': 'Failed to fetch balance'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    # ---------------------------------------------------------
    # ✅ FORMAT PHONE
    # ---------------------------------------------------------
    def format_phone_number(self, phone):
        if not phone:
            return None

        cleaned = ''.join(filter(str.isdigit, str(phone)))
        
        # Remove leading country code if present
        if cleaned.startswith('91') and len(cleaned) == 12:
            cleaned = cleaned[2:]
        
        if 10 <= len(cleaned) <= 15:
            return cleaned
        return None

    # ---------------------------------------------------------
    # ✅ VALIDATE API
    # ---------------------------------------------------------
    def validate_credentials(self):
        result = self.check_balance()
        return result.get('success', False)