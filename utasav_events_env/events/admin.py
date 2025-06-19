# admin.py
from django.contrib import admin
from .models import EventInquiry

@admin.register(EventInquiry)
class EventInquiryAdmin(admin.ModelAdmin):
    list_display = [
        'full_name', 
        'phone_number',  
        'budget_range', 
        'sms_sent_to_business',
        'sms_sent_to_customer',
        'email_sent_to_business',
        'email_sent_to_customer',
        'created_at'
    ]
    
    list_filter = [
        'event_type', 
        'budget_range', 
        'created_at',
        'sms_sent_to_business',
        'sms_sent_to_customer',
        'email_sent_to_business',
        'email_sent_to_customer'
    ]
    
    search_fields = ['full_name', 'phone_number', 'email', 'event_type']
    
    readonly_fields = [
        'created_at', 
        'sms_sent_to_business', 
        'sms_sent_to_customer',
        'email_sent_to_business',
        'email_sent_to_customer'
    ]
    
    fieldsets = (
        ('Customer Information', {
            'fields': ('full_name', 'phone_number', 'email')
        }),
        ('Event Details', {
            'fields': ('event_type', 'budget_range', 'additional_details')
        }),
        ('Notification Status', {
            'fields': (
                'sms_sent_to_business', 
                'sms_sent_to_customer',
                'email_sent_to_business',
                'email_sent_to_customer'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    # Custom methods to display notification status with colors
    def sms_business_status(self, obj):
        if obj.sms_sent_to_business:
            return "✅ Sent"
        return "❌ Failed"
    sms_business_status.short_description = "Business SMS"
    
    def sms_customer_status(self, obj):
        if obj.sms_sent_to_customer:
            return "✅ Sent"
        return "❌ Failed"
    sms_customer_status.short_description = "Customer SMS"
    
    def email_business_status(self, obj):
        if obj.email_sent_to_business:
            return "✅ Sent"
        return "❌ Failed"
    email_business_status.short_description = "Business Email"
    
    def email_customer_status(self, obj):
        if obj.email_sent_to_customer:
            return "✅ Sent"
        elif not obj.email:
            return "➖ No Email"
        return "❌ Failed"
    email_customer_status.short_description = "Customer Email"
    
    # Optional: Add actions to resend notifications
    actions = ['resend_business_notifications', 'resend_customer_notifications']
    
    def resend_business_notifications(self, request, queryset):
        from .whatsapp_service import NotificationService
        notification_service = NotificationService()
        
        success_count = 0
        for inquiry in queryset:
            try:
                # Resend SMS
                sms_success, _ = notification_service.send_business_sms_notification(inquiry)
                inquiry.sms_sent_to_business = sms_success
                
                # Resend Email
                email_success, _ = notification_service.send_business_email_notification(inquiry)
                inquiry.email_sent_to_business = email_success
                
                inquiry.save()
                
                if sms_success and email_success:
                    success_count += 1
                    
            except Exception as e:
                pass
        
        self.message_user(request, f"Attempted to resend business notifications for {queryset.count()} inquiries. {success_count} successful.")
    
    resend_business_notifications.short_description = "Resend business notifications"
    
    def resend_customer_notifications(self, request, queryset):
        from .whatsapp_service import NotificationService
        notification_service = NotificationService()
        
        success_count = 0
        for inquiry in queryset:
            try:
                # Resend SMS
                sms_success, _ = notification_service.send_customer_sms_confirmation(inquiry)
                inquiry.sms_sent_to_customer = sms_success
                
                # Resend Email (if email exists)
                email_success = False
                if inquiry.email:
                    email_success, _ = notification_service.send_customer_email_confirmation(inquiry)
                    inquiry.email_sent_to_customer = email_success
                
                inquiry.save()
                
                if sms_success and (email_success or not inquiry.email):
                    success_count += 1
                    
            except Exception as e:
                pass
        
        self.message_user(request, f"Attempted to resend customer notifications for {queryset.count()} inquiries. {success_count} successful.")
    
    resend_customer_notifications.short_description = "Resend customer notifications"