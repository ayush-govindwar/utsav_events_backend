from django.db import models
from django.utils import timezone

class EventInquiry(models.Model):
    EVENT_TYPES = [
        ('Corporate Event', 'Corporate Event'),
        ('Wedding', 'Wedding'),
        ('Birthday Party', 'Birthday Party'),
        ('Conference', 'Conference'),
        ('Product Launch', 'Product Launch'),
        ('Networking Event', 'Networking Event'),
        ('Workshop', 'Workshop'),
        ('Seminar', 'Seminar'),
        ('Exhibition', 'Exhibition'),
        ('Other', 'Other'),
    ]
    
    BUDGET_RANGES = [
        ('1-5 th', '1-5 th'),
        ('5-10 th', '5-10 th'),
        ('10-25 th', '10-25 th'),
        ('25-50 th', '25-50 th'),
        ('50-100 th', '50-100 th'),
        ('100+ th', '100+ th'),
    ]
    
    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    budget_range = models.CharField(max_length=20, choices=BUDGET_RANGES, blank=True, null=True)
    additional_details = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    sms_sent_to_business = models.BooleanField(default=False)
    sms_sent_to_customer = models.BooleanField(default=False)
    email_sent_to_business = models.BooleanField(default=False)
    email_sent_to_customer = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.full_name} - {self.event_type}"