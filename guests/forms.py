# guests/forms.py
from django import forms
from .models import Guest, GuestContact

class GuestForm(forms.ModelForm):
    class Meta:
        model = Guest
        fields = ['first_name', 'last_name', 'email', 'phone', 'date_of_birth', 'gender', 
                  'nationality', 'id_type', 'id_number', 'address', 'city', 'country', 'postal_code', 
                  'company', 'preferred_contact']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Email'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Phone Number'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'gender': forms.Select(attrs={'class': 'form-input'}),
            'nationality': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Nationality'}),
            'id_type': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'ID Type'}),
            'id_number': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'ID Number'}),
            'address': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Address'}),
            'city': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'City'}),
            'country': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Country'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Postal Code'}),
            'company': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Company'}),
            'preferred_contact': forms.TextInput(attrs={'class': 'form-input'}),
        }

class GuestContactForm(forms.ModelForm):
    class Meta:
        model = GuestContact
        fields = ['emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relation']
        widgets = {
            'emergency_contact_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Contact Name'}),
            'emergency_contact_phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Phone Number'}),
            'emergency_contact_relation': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Relation'}),
        }