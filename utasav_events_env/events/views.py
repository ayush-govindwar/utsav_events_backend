from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import EventInquiry
from .serializers import EventInquirySerializer
from .whatsapp_service import WhatsAppService
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
            
            # Generate WhatsApp URL with pre-filled message
            whatsapp_url = WhatsAppService.generate_whatsapp_url_from_inquiry_object(inquiry)
            
            # Prepare response
            response_data = {
                'message': 'Event inquiry submitted successfully!',
                'inquiry_id': inquiry.id,
                'whatsapp_url': whatsapp_url
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