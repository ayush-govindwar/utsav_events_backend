import urllib.parse
from typing import Dict, Any

class WhatsAppService:
    """Service to generate WhatsApp URLs with pre-filled messages"""
    
    BUSINESS_PHONE_NUMBER = "9284748523"  # Hardcoded business number
    
    @classmethod
    def generate_whatsapp_url(cls, inquiry_data: Dict[str, Any]) -> str:
        """
        Generate WhatsApp URL with pre-filled message containing inquiry details
        
        Args:
            inquiry_data: Dictionary containing form data
            
        Returns:
            str: WhatsApp URL with pre-filled message
        """
        message = cls._format_inquiry_message(inquiry_data)
        encoded_message = urllib.parse.quote(message)
        
        # WhatsApp URL format: https://wa.me/PHONENUMBER?text=MESSAGE
        whatsapp_url = f"https://wa.me/{cls.BUSINESS_PHONE_NUMBER}?text={encoded_message}"
        
        return whatsapp_url
    
    @classmethod
    def _format_inquiry_message(cls, inquiry_data: Dict[str, Any]) -> str:
        """
        Format inquiry data into a WhatsApp message
        
        Args:
            inquiry_data: Dictionary containing form data
            
        Returns:
            str: Formatted message string
        """
        message_parts = [
            "🎉 *Event Inquiry*",
            "",
            f"*Name:* {inquiry_data.get('full_name', 'N/A')}",
            f"*Phone:* {inquiry_data.get('phone_number', 'N/A')}",
            f"*Event Type:* {inquiry_data.get('event_type', 'N/A')}",
        ]
        
        # Add optional fields if they exist
        if inquiry_data.get('budget_range'):
            message_parts.append(f"*Budget Range:* ₹{inquiry_data['budget_range']}")
        
        # Email field is not available in the current model
        # if inquiry_data.get('email'):
        #     message_parts.append(f"*Email:* {inquiry_data['email']}")
        
        if inquiry_data.get('additional_details'):
            message_parts.extend([
                "",
                "*Additional Details:*",
                inquiry_data['additional_details']
            ])
        
        message_parts.extend([
            "",
            "Please contact me to discuss the event planning details.",
            "",
            "Thank you! 😊"
        ])
        
        return "\n".join(message_parts)
    
    @classmethod
    def generate_whatsapp_url_from_inquiry_object(cls, inquiry) -> str:
        """
        Generate WhatsApp URL from EventInquiry model instance
        
        Args:
            inquiry: EventInquiry model instance
            
        Returns:
            str: WhatsApp URL with pre-filled message
        """
        inquiry_data = {
            'full_name': inquiry.full_name,
            'phone_number': inquiry.phone_number,
            'event_type': inquiry.event_type,
            'budget_range': inquiry.budget_range,
            'email': None,  # Email field not available in current model
            'additional_details': inquiry.additional_details,
        }
        
        return cls.generate_whatsapp_url(inquiry_data)