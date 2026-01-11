# rooms/forms.py
from django import forms
from .models import Room, RoomType, HousekeepingTask
from core.models import CustomUser

class RoomTypeForm(forms.ModelForm):
    class Meta:
        model = RoomType
        fields = ['name', 'description', 'base_price', 'max_occupancy', 'amenities']
        widgets = {
            'name': forms.Select(attrs={'class': 'form-input', 'placeholder': 'Room Type Name'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Description'}),
            'base_price': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'placeholder': 'Base Price'}),
            'max_occupancy': forms.NumberInput(attrs={'class': 'form-input', 'min': '1', 'placeholder': 'Max Occupancy'}),
            'amenities': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'List amenities (comma separated)'}),
        }

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['room_number', 'floor', 'room_type', 'price_per_night', 'status', 'notes']
        widgets = {
            'room_number': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Room Number'}),
            'floor': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Floor'}),
            'room_type': forms.Select(attrs={'class': 'form-input'}),
            'price_per_night': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'placeholder': 'Price per Night'}),
            'status': forms.Select(attrs={'class': 'form-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Notes'}),
        }

class HousekeepingTaskForm(forms.ModelForm):
    class Meta:
        model = HousekeepingTask
        fields = ['room', 'task_type', 'description', 'priority', 'assigned_to', 'due_date', 'notes']
        widgets = {
            'room': forms.Select(attrs={'class': 'form-input'}),
            'task_type': forms.Select(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Task Description'}),
            'priority': forms.Select(attrs={'class': 'form-input'}),
            'assigned_to': forms.Select(attrs={'class': 'form-input'}),
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Notes'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].queryset = CustomUser.objects.filter(role='housekeeping')
        self.fields['room'].queryset = Room.objects.filter(status='available')

class UpdateTaskStatusForm(forms.ModelForm):
    class Meta:
        model = HousekeepingTask
        fields = ['status', 'notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Completion notes'}),
        }