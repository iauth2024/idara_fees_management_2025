from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError



class Student(models.Model):
    

   

    STUDENT_TYPE_CHOICES = [
        ('Day Scholar', 'Day Scholar'),
        ('Boarder', 'Boarder'),
    ]

    
    admission_number = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    father_name = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    course = models.CharField(max_length=100)  # ✅ now dynamic
    section = models.CharField(max_length=100)
    branch = models.CharField(max_length=100)
    monthly_fees = models.DecimalField(max_digits=10, decimal_places=2)
    student_type = models.CharField(max_length=20, choices=STUDENT_TYPE_CHOICES, default='Boarder')

    @property
    def total_fees(self):
        return self.monthly_fees * 12

    def __str__(self):
        return f'{self.name} ({self.admission_number})'


class Payment(models.Model):
    RECEIPT_TYPE_CHOICES = [
        ('fee', 'Fee'),
        ('donation', 'Donation'),
        ('other', 'Other'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('online', 'Online'),
    ]

    receipt_no = models.CharField(max_length=20, null=False, blank=False, unique=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    receipt_type = models.CharField(max_length=15, choices=RECEIPT_TYPE_CHOICES, default='fee')
    name = models.CharField(max_length=255, null=True, blank=True)
    payment_method = models.CharField(max_length=100, choices=PAYMENT_METHOD_CHOICES, default='cash')
    organization = models.CharField(max_length=255, null=True, blank=True)
    year = models.CharField(max_length=9, null=True, blank=True)

    class Meta:
        unique_together = ('receipt_no',)

    def __str__(self):
        return f'Receipt No: {self.receipt_no}'


 
