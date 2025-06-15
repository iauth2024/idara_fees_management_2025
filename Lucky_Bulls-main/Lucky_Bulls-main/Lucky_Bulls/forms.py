from django import forms
from .models import TradingAccount

class TradingAccountForm(forms.ModelForm):
    class Meta:
        model = TradingAccount
        fields = ['name', 'client_id', 'token', 'is_master', 'is_child', 'parent_account', 'multiplier']
        
        widgets = {
            'token': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter API token...'}),
            'multiplier': forms.NumberInput(attrs={'step': '0.01', 'min': '0.1'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        is_master = cleaned_data.get('is_master')
        is_child = cleaned_data.get('is_child')
        parent_account = cleaned_data.get('parent_account')

        # Prevent both is_master and is_child from being selected at the same time
        if is_master and is_child:
            raise forms.ValidationError("An account cannot be both a master and a child.")

        # Ensure child accounts must have a parent
        if is_child and not parent_account:
            raise forms.ValidationError("A child account must have a parent account.")

        # Ensure master accounts cannot have a parent
        if is_master and parent_account:
            raise forms.ValidationError("A master account cannot have a parent account.")

        return cleaned_data

from .models import Screener

class ScreenerForm(forms.ModelForm):
    class Meta:
        model = Screener
        fields = ['name', 'condition', 'is_active'] 