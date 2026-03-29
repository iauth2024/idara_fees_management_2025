# sms_templates.py
from datetime import datetime
from decimal import Decimal

class SMSTemplates:
    
    # Institute name
    INSTITUTE_NAME = "Idara Ashraful Uloom"
    
    @staticmethod
    def donation_due_reminder(admission_no, student_name, due_amount, institute_name=None):
        """
        Template for donation due reminder (Non-DLT - can be flexible)
        """
        inst = institute_name or SMSTemplates.INSTITUTE_NAME
        amount_formatted = f"{int(due_amount):,}"
        
        message = (f"Dear Parent, Donation due for Admission No: {admission_no}, "
                  f"Name: {student_name} is Rs {amount_formatted}. "
                  f"Kindly ignore if already paid. Thank you. - {inst}")
        return message
    
    @staticmethod
    def fee_due_reminder(student_name, due_amount, months_due, admission_no):
        """
        ✅ DLT APPROVED TEMPLATE (STRICT - DO NOT MODIFY TEXT)
        
        Template:
        Fee due of Rs {#var#} for {#var#} month(s) for {#var#} (Adm No:{#var#}) pending. Ignore if paid. Idara Ashraful Uloom
        """
        # ⚠️ DLT SAFE FORMATTING - No commas, no special characters
        amount = int(due_amount)  # No commas
        months = int(months_due)
        
        message = (
            f"Fee due of Rs {amount} for {months} month(s) "
            f"for {student_name} (Adm No:{admission_no}) pending. "
            f"Ignore if paid. Idara Ashraful Uloom"
        )
        
        return message
    
    @staticmethod
    def urgent_reminder(student_name, due_amount, months_due, institute_name=None):
        """
        Urgent reminder (Non-DLT)
        """
        inst = institute_name or SMSTemplates.INSTITUTE_NAME
        amount_formatted = f"{due_amount:,.0f}"
        
        message = (f"URGENT: Dear {student_name}, your fee of Rs. {amount_formatted} is overdue "
                  f"by {months_due} months. Immediate payment required to continue classes. - {inst}")
        return message
    
    @staticmethod
    def payment_confirmation(student_name, amount_paid, month, institute_name=None):
        """
        Payment confirmation (Non-DLT unless approved separately)
        """
        inst = institute_name or SMSTemplates.INSTITUTE_NAME
        amount_formatted = f"{amount_paid:,.0f}"
        
        message = (f"Dear {student_name}, thank you for your payment of Rs. {amount_formatted} "
                  f"for {month}. Your account is updated. - {inst}")
        return message
    
    @staticmethod
    def get_message_length(message):
        """Get message length"""
        return len(message)
    
    @staticmethod
    def validate_message(message, max_length=160):
        """Validate message length"""
        length = len(message)
        return {
            'valid': length <= max_length,
            'length': length,
            'max_length': max_length,
            'exceeds_by': max(0, length - max_length)
        }