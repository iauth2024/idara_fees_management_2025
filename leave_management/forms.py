# forms.py
from django import forms
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .models import LeaveRequest, LeaveReason  # assuming these models exist


class LeaveRequestForm(forms.ModelForm):
    admission_number = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter admission number (e.g. STU12345)'),
            'autocomplete': 'off',
            'autofocus': 'autofocus',
        }),
        label=_("Admission Number"),
        error_messages={
            'required': _('Please enter an admission number.'),
            'max_length': _('Admission number must be at most 50 characters.'),
        }
    )

    start_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
        }),
        initial=timezone.localdate,
        label=_("Start Date"),
        error_messages={
            'required': _('Please select a start date.'),
            'invalid': _('Please enter a valid date.'),
        }
    )

    start_time = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'type': 'time',
            'class': 'form-control',
        }),
        initial='09:00',
        label=_("Start Time"),
        error_messages={
            'required': _('Please select a start time.'),
            'invalid': _('Please enter a valid time.'),
        }
    )

    end_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
        }),
        initial=timezone.localdate,
        label=_("End Date"),
        error_messages={
            'required': _('Please select an end date.'),
            'invalid': _('Please enter a valid date.'),
        }
    )

    end_time = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'type': 'time',
            'class': 'form-control',
        }),
        initial='17:00',
        label=_("End Time"),
        error_messages={
            'required': _('Please select an end time.'),
            'invalid': _('Please enter a valid time.'),
        }
    )

    reason = forms.ModelChoiceField(
        queryset=LeaveReason.objects.all().order_by('name'),
        empty_label=_("— Select reason —"),
        widget=forms.Select(attrs={
            'class': 'form-control',
        }),
        label=_("Leave Reason"),
        error_messages={
            'required': _('Please select a reason for leave.'),
            'invalid_choice': _('Please select a valid reason.'),
        }
    )

    notes = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': _('Additional notes or special requests (optional)...'),
        }),
        required=False,
        max_length=500,
        label=_("Additional Notes"),
        error_messages={
            'max_length': _('Notes must be at most 500 characters.'),
        }
    )

    class Meta:
        model = LeaveRequest
        fields = [
            'admission_number',
            'start_date', 'start_time',
            'end_date', 'end_time',
            'reason',
            'notes',
        ]

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if start_date and end_date:
            if end_date < start_date:
                raise forms.ValidationError(
                    _("End date cannot be before start date.")
                )

            if start_date == end_date and start_time and end_time:
                if end_time <= start_time:
                    raise forms.ValidationError(
                        _("On the same day, end time must be after start time.")
                    )

        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add help text for fields
        self.fields['admission_number'].help_text = _(
            'Enter the student\'s admission number. Press Tab to auto-fill details.'
        )
        self.fields['start_date'].help_text = _('Select the date when leave begins.')
        self.fields['end_date'].help_text = _('Select the date when leave ends.')
        self.fields['reason'].help_text = _('Choose the reason for leave from the list.')
        self.fields['notes'].help_text = _('Optional: Add any special instructions or remarks.')


# Optional: Add a separate form for check-in
class CheckInForm(forms.Form):
    checkin_datetime = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control',
        }),
        label=_("Check-In Date & Time"),
        initial=timezone.now,
        error_messages={
            'required': _('Please select check-in date and time.'),
            'invalid': _('Please enter a valid date and time.'),
        }
    )
    
    notes = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': _('Optional remarks or observations...'),
        }),
        required=False,
        max_length=250,
        label=_("Notes (Optional)"),
        error_messages={
            'max_length': _('Notes must be at most 250 characters.'),
        }
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['checkin_datetime'].help_text = _(
            'Select the actual date and time of student check-in.'
        )
        self.fields['notes'].help_text = _(
            'Add any remarks about late return, early check-in, etc.'
        )


# Optional: Form for filtering leave reports
class LeaveReportFilterForm(forms.Form):
    adm_no = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter admission number'),
        }),
        label=_("Admission Number")
    )
    
    name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter student name'),
        }),
        label=_("Student Name")
    )
    
    branch = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter branch'),
        }),
        label=_("Branch")
    )
    
    from_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
        }),
        label=_("From Date")
    )
    
    to_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
        }),
        label=_("To Date")
    )
    
    status = forms.ChoiceField(
        required=False,
        choices=[
            ('', _('All Statuses')),
            ('pending', _('Pending')),
            ('approved', _('Approved')),
            ('rejected', _('Rejected')),
            ('checked_in', _('Checked In')),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control',
        }),
        label=_("Status")
    )

    def clean(self):
        cleaned_data = super().clean()
        from_date = cleaned_data.get('from_date')
        to_date = cleaned_data.get('to_date')
        
        if from_date and to_date and to_date < from_date:
            raise forms.ValidationError(
                _("To date cannot be before from date.")
            )
        
        return cleaned_data