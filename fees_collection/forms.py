# forms.py

from django import forms
from .models import Payment

class PaymentForm(forms.Form):
    admission_number = forms.CharField(label="Admission Number")
    amount_paid = forms.DecimalField(label="Amount Paid")
    receipt_number = forms.CharField(label="Receipt Number")
    date= forms.DateField(label="Date")
    created_by = forms.CharField(label="Created By")
    payment_method = forms.CharField(label="Payment Method")

class UploadFileForm(forms.Form):
    file = forms.FileField(label='Select a file')
class PaymentUploadForm(forms.Form):
    excel_file = forms.FileField()


from django import forms
from .models import Student

class StudentEditForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'father_name', 'phone', 'course', 'branch', 'section', 'student_type']  # Exclude admission_number and fees
