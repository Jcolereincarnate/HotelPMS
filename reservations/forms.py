# reservations/forms.py
from django import forms
from django.utils import timezone
from .models import Reservation, ReservationAddon
from guests.models import Guest
from rooms.models import Room
class ReservationForm(forms.ModelForm):
    guest = forms.ModelChoiceField(
        queryset=Guest.objects.all(),
        widget=forms.Select(attrs={'class': 'form-input'})
    )
    room = forms.ModelChoiceField(
        queryset=Room.objects.filter(status='available'),
        widget=forms.Select(attrs={'class': 'form-input'})
    )
    
    class Meta:
        model = Reservation
        fields = ['guest', 'room', 'check_in_date', 'check_out_date', 'number_of_guests', 'number_of_children', 'special_requests']
        widgets = {
            'check_in_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'check_out_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'number_of_guests': forms.NumberInput(attrs={'class': 'form-input', 'min': '1'}),
            'number_of_children': forms.NumberInput(attrs={'class': 'form-input', 'min': '0'}),
            'special_requests': forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'Any special requests...'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get('check_in_date')
        check_out = cleaned_data.get('check_out_date')
        
        if check_in and check_out:
            if check_in >= check_out:
                raise forms.ValidationError("Check-out date must be after check-in date.")
            if check_in < timezone.now().date():
                raise forms.ValidationError("Check-in date cannot be in the past.")
        
        return cleaned_data

class CheckInForm(forms.Form):
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('bank_transfer', 'Bank Transfer'),
    ]

    notes = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Check-in notes...'}), required=False)

class CheckOutForm(forms.Form):
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('paystack', 'Paystack'),
    ]

    notes = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Check-out notes...'}), required=False)