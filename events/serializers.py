from rest_framework import serializers
from .models import EventInquiry

class EventInquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = EventInquiry
        fields = ['full_name', 'phone_number', 'email', 'event_type', 'budget_range', 'additional_details']
        extra_kwargs = {
            'email': {'required': False, 'allow_blank': True},
            'budget_range': {'required': False, 'allow_blank': True},
            'additional_details': {'required': False, 'allow_blank': True},
        }
    
    def validate_phone_number(self, value):
        if not value.isdigit() or len(value) != 10:
            raise serializers.ValidationError("Phone number must be 10 digits")
        return value
    
    def validate_email(self, value):
        if value and not value.strip():
            return None
        return value