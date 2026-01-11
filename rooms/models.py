from django.db import models
from django.core.validators import MinValueValidator
import uuid

class RoomType(models.Model):
    NAME_CHOICES = [
        ('single', 'Single'),
        ('double', 'Double'),
        ('suite', 'Suite'),
    ]
    name = models.CharField(max_length=100, choices=NAME_CHOICES) 
    description = models.TextField(blank=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    max_occupancy = models.IntegerField(validators=[MinValueValidator(1)])
    amenities = models.TextField(blank=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Room(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('reserved', 'Reserved'),
        ('occupied', 'Occupied'),
        ('maintenance', 'Maintenance'),
        ('cleaning', 'Cleaning'),
        ('blocked', 'Blocked'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room_number = models.CharField(max_length=20, unique=True)
    floor = models.IntegerField()
    room_type = models.ForeignKey(RoomType, on_delete=models.PROTECT, related_name='rooms')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['floor', 'room_number']
        indexes = [
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Room {self.room_number}"

class HousekeepingTask(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    TASK_CHOICES = [
        ('cleaning', 'Cleaning'),
        ('maintenance', 'Maintenance'),
        ('inspection', 'Inspection'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='housekeeping_tasks')
    task_type = models.CharField(max_length=100, choices=TASK_CHOICES)
    description = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    assigned_to = models.ForeignKey('core.CustomUser', null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    completed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-priority', 'due_date']
    
    def __str__(self):
        return f"{self.task_type} - Room {self.room.room_number}"