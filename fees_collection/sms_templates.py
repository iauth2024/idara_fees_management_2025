# sms_templates.py
from datetime import datetime
from decimal import Decimal

class SMSTemplates:
    
    # Institute name constant for easy updates
    INSTITUTE_NAME = "Institute"  # Change this to your actual institute name
    
    @staticmethod
    def donation_due_reminder(admission_no, student_name, due_amount, institute_name=None):
        """
        Template for donation due reminder
        """
        inst = institute_name or SMSTemplates.INSTITUTE_NAME
        # Format amount with commas for thousands
        amount_formatted = f"{int(due_amount):,}"
        
        message = (f"Dear Parent, Donation due for Admission No: {admission_no}, "
                  f"Name: {student_name} is Rs {amount_formatted}. "
                  f"Kindly ignore if already paid. Thank you. - {inst}")
        return message
    
    @staticmethod
    def fee_due_reminder(student_name, due_amount, months_due, due_date=None, institute_name=None):
        """
        Template for fee due reminder
        """
        inst = institute_name or SMSTemplates.INSTITUTE_NAME
        amount_formatted = f"{due_amount:,.0f}"
        
        if due_date:
            if isinstance(due_date, str):
                date_str = due_date
            else:
                date_str = due_date.strftime('%d-%m-%Y')
                
            message = (f"Dear {student_name}, your fee of Rs. {amount_formatted} is due "
                      f"for {months_due} month(s). Please pay by {date_str} to avoid late fee. - {inst}")
        else:
            message = (f"Dear {student_name}, your fee of Rs. {amount_formatted} is due "
                      f"for {months_due} month(s). Please clear your dues at earliest. - {inst}")
        
        return message
    
    @staticmethod
    def urgent_reminder(student_name, due_amount, months_due, institute_name=None):
        """
        Urgent reminder for long overdue
        """
        inst = institute_name or SMSTemplates.INSTITUTE_NAME
        amount_formatted = f"{due_amount:,.0f}"
        
        message = (f"URGENT: Dear {student_name}, your fee of Rs. {amount_formatted} is overdue "
                  f"by {months_due} months. Immediate payment required to continue classes. - {inst}")
        return message
    
    @staticmethod
    def payment_confirmation(student_name, amount_paid, month, institute_name=None):
        """
        Payment confirmation template
        """
        inst = institute_name or SMSTemplates.INSTITUTE_NAME
        amount_formatted = f"{amount_paid:,.0f}"
        
        message = (f"Dear {student_name}, thank you for your payment of Rs. {amount_formatted} "
                  f"for {month}. Your account is updated. - {inst}")
        return message
    
    @staticmethod
    def get_message_length(message):
        """
        Helper method to check SMS length (useful for debugging)
        """
        return len(message)
    
    @staticmethod
    def validate_message(message, max_length=160):
        """
        Validate if message exceeds SMS character limit
        """
        length = len(message)
        return {
            'valid': length <= max_length,
            'length': length,
            'max_length': max_length,
            'exceeds_by': max(0, length - max_length)
        }