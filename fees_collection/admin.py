from django.contrib import admin
from .models import Student, Payment

# Admin configuration for the Student model
class StudentAdmin(admin.ModelAdmin):
    list_display = ['admission_number', 'name', 'phone', 'course', 'branch', 'section', 'monthly_fees', 'student_type']
    list_filter = ['course', 'branch', 'section', 'student_type']
    search_fields = ['admission_number', 'name', 'phone']

# Register the Student model with the StudentAdmin configuration
admin.site.register(Student, StudentAdmin)

# Admin configuration for the Payment model
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('receipt_no', 'student', 'amount', 'date', 'created_by', 'receipt_type', 'name', 'payment_method', 'organization', 'year')
    search_fields = ['student__admission_number', 'receipt_no']

# This ensures both the Student and Payment models are properly visible and manageable in the Django admin interface.
