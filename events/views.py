from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import EventInquiry
from .serializers import EventInquirySerializer
from .whatsapp_service import WhatsAppService
from .email_service import EmailService
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
def submit_event_inquiry(request):
    """Handle event inquiry submission"""
    serializer = EventInquirySerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            # Save inquiry to database
            inquiry = serializer.save()
            
            # Initialize services
            email_service = EmailService()
            
            # Send email notifications in background
            try:
                # Send business email notification
                business_email_success, business_email_message = email_service.send_business_email_notification(inquiry)
                inquiry.email_sent_to_business = business_email_success
                
                # Send customer email confirmation (only if email provided)
                if inquiry.email:
                    customer_email_success, customer_email_message = email_service.send_customer_email_confirmation(inquiry)
                    inquiry.email_sent_to_customer = customer_email_success
                else:
                    customer_email_success = True  # No email to send, so consider it successful
                    customer_email_message = "No customer email provided"
                
                # Update inquiry with email status
                inquiry.save()
                
                logger.info(f"Email notifications processed for inquiry {inquiry.id}: Business={business_email_success}, Customer={customer_email_success}")
                
            except Exception as email_error:
                logger.error(f"Error sending email notifications for inquiry {inquiry.id}: {str(email_error)}")
                # Don't fail the whole request if email fails
            
            # Generate WhatsApp URL with pre-filled message
            whatsapp_url = WhatsAppService.generate_whatsapp_url_from_inquiry_object(inquiry)
            
            # Prepare response
            response_data = {
                'message': 'Event inquiry submitted successfully!',
                'inquiry_id': inquiry.id,
                'whatsapp_url': whatsapp_url,
                'email_status': {
                    'business_email_sent': inquiry.email_sent_to_business,
                    'customer_email_sent': inquiry.email_sent_to_customer if inquiry.email else None
                }
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error processing event inquiry: {str(e)}")
            return Response(
                {'error': 'An error occurred while processing your inquiry. Please try again.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def health_check(request):
    """Simple health check endpoint"""
    return Response({'status': 'OK', 'message': 'Events API is running'})

@api_view(['POST'])
def generate_whatsapp_url(request):
    """Generate WhatsApp URL for form data without saving to database"""
    try:
        # Generate WhatsApp URL directly from request data
        whatsapp_url = WhatsAppService.generate_whatsapp_url(request.data)
        
        return Response({
            'whatsapp_url': whatsapp_url,
            'message': 'WhatsApp URL generated successfully'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error generating WhatsApp URL: {str(e)}")
        return Response(
            {'error': 'An error occurred while generating WhatsApp URL'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
def resend_email_notifications(request, inquiry_id):
    """Resend email notifications for a specific inquiry"""
    try:
        inquiry = EventInquiry.objects.get(id=inquiry_id)
        email_service = EmailService()
        
        # Resend business email
        business_success, business_message = email_service.send_business_email_notification(inquiry)
        inquiry.email_sent_to_business = business_success
        
        # Resend customer email if email exists
        customer_success = True
        customer_message = "No customer email provided"
        if inquiry.email:
            customer_success, customer_message = email_service.send_customer_email_confirmation(inquiry)
            inquiry.email_sent_to_customer = customer_success
        
        inquiry.save()
        
        return Response({
            'message': 'Email notifications resent',
            'business_email': {
                'success': business_success,
                'message': business_message
            },
            'customer_email': {
                'success': customer_success,
                'message': customer_message
            }
        }, status=status.HTTP_200_OK)
        
    except EventInquiry.DoesNotExist:
        return Response(
            {'error': 'Inquiry not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error resending email notifications: {str(e)}")
        return Response(
            {'error': 'Failed to resend email notifications'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )