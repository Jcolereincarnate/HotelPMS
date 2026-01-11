from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
import uuid
class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('manager', 'Manager'),
        ('receptionist', 'Receptionist'),
        ('housekeeping', 'Housekeeping Staff'),
        ('accounting', 'Accounting Staff'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='receptionist')
    phone = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['username']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"

class Hotel(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    currency = models.CharField(max_length=3, default='NGN')
    timezone = models.CharField(max_length=50, default='Africa/Lagos')
    check_in_time = models.TimeField(default='14:00')
    check_out_time = models.TimeField(default='11:00')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name