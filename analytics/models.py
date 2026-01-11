from django.db import models
import uuid
import json
from django.db.models import Sum
class AIReport(models.Model):
    REPORT_TYPE_CHOICES = [
        ('occupancy', 'Occupancy Analysis'),
        ('revenue', 'Revenue Forecast'),
        ('guest_insights', 'Guest Insights'),
        ('trends', 'Booking Trends'),
        ('recommendations', 'Smart Recommendations'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report_type = models.CharField(max_length=50, choices=REPORT_TYPE_CHOICES)
    title = models.CharField(max_length=255)
    summary = models.TextField()
    data = models.JSONField()  
    insights = models.JSONField()  
    recommendations = models.JSONField() 
    created_at = models.DateTimeField(auto_now_add=True)
    generated_by = models.CharField(max_length=100, default='AI Analytics Engine')
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_report_type_display()} - {self.created_at.date()}"

class DailyMetrics(models.Model):
    date = models.DateField(unique=True, db_index=True)
    total_rooms = models.IntegerField()
    occupied_rooms = models.IntegerField()
    available_rooms = models.IntegerField()
    occupancy_rate = models.FloatField()  # Percentage
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2)
    guest_count = models.IntegerField()
    check_ins = models.IntegerField()
    check_outs = models.IntegerField()
    cancellations = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"Metrics for {self.date}"