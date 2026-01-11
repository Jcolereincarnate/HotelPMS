from django.db import models
from django.utils import timezone
import uuid

class Reservation(models.Model):
    STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('checked_in', 'Checked In'),
        ('checked_out', 'Checked Out'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    guest = models.ForeignKey('guests.Guest', on_delete=models.PROTECT, related_name='reservations')
    room = models.ForeignKey('rooms.Room', on_delete=models.PROTECT, related_name='reservations')
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    number_of_guests = models.IntegerField()
    number_of_children = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    special_requests = models.TextField(blank=True)
    created_by = models.ForeignKey('core.CustomUser', on_delete=models.SET_NULL, null=True, related_name='reservations_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    checked_in_at = models.DateTimeField(null=True, blank=True)
    checked_out_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['check_in_date', 'check_out_date']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.guest.first_name} - Room {self.room.room_number} ({self.check_in_date})"
    
    def is_active(self):
        today = timezone.now().date()
        return self.check_in_date <= today <= self.check_out_date

class ReservationAddon(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name='addons')
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(default=1)
    
    def __str__(self):
        return f"{self.name} x{self.quantity} for {self.reservation.guest.first_name} {self.reservation.guest.last_name}"