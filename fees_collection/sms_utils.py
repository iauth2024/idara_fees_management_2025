# sms_utils.py
import requests
import json
from urllib.parse import quote
import logging

logger = logging.getLogger(__name__)

class SMSAPI:
    def __init__(self):
        self.username = 'AUTHYD1'
        self.api_key = '41ae060366d9807b68a0'
        self.base_url = 'https://smslogin.co/v3/api.php'
        self.sender_id = 'AUTHYD'  # Your approved sender ID
        self.template_id = '1707169891807705976'  # Use "Receipt" template for fee reminders
        
    def send_sms(self, mobile_numbers, message, template_id=None):
        """
        Send SMS to single or multiple mobile numbers
        
        Args:
            mobile_numbers: Single number or list of numbers
            message: SMS message content
            template_id: Optional template ID (uses default if not provided)
            
        Returns:
            dict: {
                'success': bool,
                'response': raw response text (optional),
                'message_id': message ID if successful (optional),
                'error': error message if failed (optional)
            }
        """
        try:
            # Use default template if none provided
            if template_id is None:
                template_id = self.template_id
            
            # Convert to comma-separated string if list
            if isinstance(mobile_numbers, list):
                # Clean and validate numbers
                clean_numbers = []
                for num in mobile_numbers:
                    # Remove any non-numeric characters
                    clean_num = ''.join(filter(str.isdigit, str(num)))
                    if clean_num and len(clean_num) >= 10:  # Basic validation
                        clean_numbers.append(clean_num)
                
                if not clean_numbers:
                    return {
                        'success': False,
                        'error': 'No valid mobile numbers provided'
                    }
                    
                mobile = ','.join(clean_numbers)
            else:
                # Clean single number
                mobile = ''.join(filter(str.isdigit, str(mobile_numbers)))
                if not mobile or len(mobile) < 10:
                    return {
                        'success': False,
                        'error': f'Invalid mobile number: {mobile_numbers}'
                    }
            
            # Encode message for URL
            encoded_message = quote(message)
            
            # Build URL with template_id (REQUIRED for DLT)
            url = (f"{self.base_url}?username={self.username}"
                   f"&apikey={self.api_key}"
                   f"&senderid={self.sender_id}"
                   f"&mobile={mobile}"
                   f"&message={encoded_message}"
                   f"&templateid={template_id}")
            
            logger.info(f"Sending SMS to {mobile}")
            logger.debug(f"URL: {url}")
            
            # Make request with timeout
            response = requests.get(url, timeout=30)
            
            logger.info(f"Response status: {response.status_code}")
            logger.debug(f"Response text: {response.text}")
            
            if response.status_code == 200:
                response_text = response.text.strip()
                
                # Check if response contains error
                if 'Error' in response_text or 'error' in response_text.lower():
                    error_msg = response_text
                    # Try to parse JSON error if possible
                    try:
                        error_data = json.loads(response_text)
                        if isinstance(error_data, dict) and 'error' in error_data:
                            error_msg = error_data['error']
                    except:
                        pass
                        
                    logger.error(f"SMS API returned error: {error_msg}")
                    return {
                        'success': False,
                        'error': error_msg
                    }
                
                # Success - response should be message ID
                logger.info(f"SMS sent successfully to {mobile}")
                return {
                    'success': True,
                    'response': response_text,
                    'message_id': response_text  # API returns message ID on success
                }
            else:
                logger.error(f"SMS failed with status {response.status_code}: {response.text}")
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}"
                }
                
        except requests.exceptions.Timeout:
            logger.error("SMS request timed out")
            return {
                'success': False,
                'error': 'Request timed out'
            }
        except requests.exceptions.ConnectionError:
            logger.error("Connection error while sending SMS")
            return {
                'success': False,
                'error': 'Connection error'
            }
        except Exception as e:
            logger.exception(f"Exception while sending SMS: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def check_balance(self):
        """
        Check available SMS credits
        
        Returns:
            dict: {
                'success': bool,
                'credits': number of credits (if successful),
                'error': error message (if failed)
            }
        """
        try:
            url = f"{self.base_url}?username={self.username}&apikey={self.api_key}"
            logger.info(f"Checking balance at: {url}")
            
            response = requests.get(url, timeout=10)
            
            logger.info(f"Balance response status: {response.status_code}")
            logger.debug(f"Balance response text: {response.text}")
            
            if response.status_code == 200:
                response_text = response.text.strip()
                
                # Try to parse as JSON first (based on PHP example)
                try:
                    data = json.loads(response_text)
                    
                    # Check for Credits field (as in the PHP example)
                    if isinstance(data, dict):
                        # Try different possible field names
                        credits = (data.get('Credits') or 
                                  data.get('credits') or 
                                  data.get('balance') or 
                                  data.get('Credit'))
                        
                        if credits is not None:
                            return {
                                'success': True,
                                'credits': str(credits),
                                'raw_data': data
                            }
                            
                except json.JSONDecodeError:
                    # Not JSON, try plain text
                    pass
                
                # Check if response is a number (simple credit response)
                if response_text.isdigit():
                    return {
                        'success': True,
                        'credits': response_text
                    }
                else:
                    # Return as is with warning
                    logger.warning(f"Unexpected balance response format: {response_text}")
                    return {
                        'success': True,
                        'credits': response_text,
                        'warning': 'Unexpected response format'
                    }
            else:
                logger.error(f"Balance check failed with status {response.status_code}")
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}"
                }
                
        except requests.exceptions.Timeout:
            logger.error("Balance check timed out")
            return {
                'success': False,
                'error': 'Request timed out'
            }
        except requests.exceptions.ConnectionError:
            logger.error("Connection error during balance check")
            return {
                'success': False,
                'error': 'Connection error'
            }
        except Exception as e:
            logger.exception(f"Exception while checking balance: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def validate_credentials(self):
        """
        Validate API credentials by checking balance
        
        Returns:
            bool: True if credentials are valid
        """
        result = self.check_balance()
        return result.get('success', False)
    
    def format_phone_number(self, phone):
        """
        Format and validate phone number
        
        Args:
            phone: Raw phone number
            
        Returns:
            str: Cleaned phone number or None if invalid
        """
        if not phone:
            return None
            
        # Remove all non-numeric characters
        cleaned = ''.join(filter(str.isdigit, str(phone)))
        
        # Basic validation (adjust as needed for your country)
        if len(cleaned) >= 10 and len(cleaned) <= 15:
            return cleaned
        
        return None