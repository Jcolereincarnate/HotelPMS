# billing/forms.py
from django import forms
from .models import Folio, Payment, FolioLineItem

class FolioForm(forms.ModelForm):
    class Meta:
        model = Folio
        fields = ['status', 'service_charges', 'discount']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-input'}),
            'service_charges': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'placeholder': 'Service Charges'}),
            'discount': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'placeholder': 'Discount Amount'}),
        }

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount', 'payment_method', 'notes']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'placeholder': 'Amount', "readonly": 'readonly'} ),
            'payment_method': forms.Select(attrs={'class': 'form-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Payment notes'}),
        }

class FolioLineItemForm(forms.ModelForm):
    class Meta:
        model = FolioLineItem
        fields = ['description', 'amount', 'quantity']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Charge Description'}),
            'amount': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'placeholder': 'Amount'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-input', 'min': '1', 'placeholder': 'Quantity'}),
        }