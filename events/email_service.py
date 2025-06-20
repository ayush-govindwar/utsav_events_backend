import os
import logging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, To, From, Subject, HtmlContent, PlainTextContent
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.sendgrid_api_key = getattr(settings, 'SENDGRID_API_KEY', os.getenv('SENDGRID_API_KEY'))
        self.from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@yourdomain.com')
        self.business_email = getattr(settings, 'BUSINESS_EMAIL', 'business@yourdomain.com')
        
        if not self.sendgrid_api_key:
            logger.error("SendGrid API key not found in settings or environment variables")
            
    def send_business_email_notification(self, inquiry):
        """Send email notification to business about new inquiry"""
        try:
            if not self.sendgrid_api_key:
                return False, "SendGrid API key not configured"
            
            # Email content
            subject = f"New Event Inquiry - {inquiry.event_type}"
            
            # HTML content
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">
                        New Event Inquiry Received
                    </h2>
                    
                    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="color: #2980b9; margin-top: 0;">Customer Details</h3>
                        <p><strong>Name:</strong> {inquiry.full_name}</p>
                        <p><strong>Phone:</strong> {inquiry.phone_number}</p>
                        <p><strong>Email:</strong> {inquiry.email if inquiry.email else 'Not provided'}</p>
                    </div>
                    
                    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="color: #2980b9; margin-top: 0;">Event Details</h3>
                        <p><strong>Event Type:</strong> {inquiry.event_type}</p>
                        <p><strong>Budget Range:</strong> {inquiry.budget_range if inquiry.budget_range else 'Not specified'}</p>
                        {f'<p><strong>Additional Details:</strong> {inquiry.additional_details}</p>' if inquiry.additional_details else ''}
                    </div>
                    
                    <div style="background-color: #e8f5e8; padding: 15px; border-radius: 5px; border-left: 4px solid #27ae60;">
                        <p style="margin: 0;"><strong>Inquiry submitted on:</strong> {inquiry.created_at.strftime('%B %d, %Y at %I:%M %p')}</p>
                    </div>
                    
                    <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 12px; color: #666;">
                        <p>This is an automated notification from your event inquiry system.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Plain text content (fallback)
            plain_content = f"""
            New Event Inquiry Received
            
            Customer Details:
            Name: {inquiry.full_name}
            Phone: {inquiry.phone_number}
            Email: {inquiry.email if inquiry.email else 'Not provided'}
            
            Event Details:
            Event Type: {inquiry.event_type}
            Budget Range: {inquiry.budget_range if inquiry.budget_range else 'Not specified'}
            {f'Additional Details: {inquiry.additional_details}' if inquiry.additional_details else ''}
            
            Inquiry submitted on: {inquiry.created_at.strftime('%B %d, %Y at %I:%M %p')}
            """
            
            # Create message
            message = Mail(
                from_email=From(self.from_email, "Event Inquiry System"),
                to_emails=To(self.business_email),
                subject=Subject(subject),
                html_content=HtmlContent(html_content),
                plain_text_content=PlainTextContent(plain_content)
            )
            
            # Send email
            sg = SendGridAPIClient(api_key=self.sendgrid_api_key)
            response = sg.send(message)
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"Business email sent successfully for inquiry {inquiry.id}")
                return True, "Email sent successfully"
            else:
                logger.error(f"Failed to send business email for inquiry {inquiry.id}. Status: {response.status_code}")
                return False, f"Failed to send email. Status: {response.status_code}"
                
        except Exception as e:
            logger.error(f"Error sending business email for inquiry {inquiry.id}: {str(e)}")
            return False, f"Error sending email: {str(e)}"
    
    def send_customer_email_confirmation(self, inquiry):
        """Send confirmation email to customer"""
        try:
            if not self.sendgrid_api_key:
                return False, "SendGrid API key not configured"
            
            if not inquiry.email:
                return False, "Customer email not provided"
            
            # Email content
            subject = "Thank you for your event inquiry!"
            
            # HTML content
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">
                        Thank You for Your Inquiry!
                    </h2>
                    
                    <p>Dear {inquiry.full_name},</p>
                    
                    <p>Thank you for reaching out to us regarding your <strong>{inquiry.event_type}</strong> event. We have received your inquiry and our team will get back to you shortly.</p>
                    
                    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="color: #2980b9; margin-top: 0;">Your Inquiry Details</h3>
                        <p><strong>Event Type:</strong> {inquiry.event_type}</p>
                        <p><strong>Budget Range:</strong> {inquiry.budget_range if inquiry.budget_range else 'Not specified'}</p>
                        {f'<p><strong>Additional Details:</strong> {inquiry.additional_details}</p>' if inquiry.additional_details else ''}
                        <p><strong>Submitted on:</strong> {inquiry.created_at.strftime('%B %d, %Y at %I:%M %p')}</p>
                    </div>
                    
                    <div style="background-color: #e8f5e8; padding: 15px; border-radius: 5px; border-left: 4px solid #27ae60;">
                        <p style="margin: 0;"><strong>What's Next?</strong></p>
                        <p style="margin: 5px 0 0 0;">Our event planning team will review your requirements and contact you within 24 hours to discuss your event details and provide a customized proposal.</p>
                    </div>
                    
                    <p style="margin-top: 20px;">If you have any urgent questions, please don't hesitate to contact us directly.</p>
                    
                    <p>Best regards,<br>
                    <strong>The Event Planning Team</strong></p>
                    
                    <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 12px; color: #666;">
                        <p>This is an automated confirmation email. Please do not reply to this email.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Plain text content (fallback)
            plain_content = f"""
            Thank You for Your Inquiry!
            
            Dear {inquiry.full_name},
            
            Thank you for reaching out to us regarding your {inquiry.event_type} event. We have received your inquiry and our team will get back to you shortly.
            
            Your Inquiry Details:
            Event Type: {inquiry.event_type}
            Budget Range: {inquiry.budget_range if inquiry.budget_range else 'Not specified'}
            {f'Additional Details: {inquiry.additional_details}' if inquiry.additional_details else ''}
            Submitted on: {inquiry.created_at.strftime('%B %d, %Y at %I:%M %p')}
            
            What's Next?
            Our event planning team will review your requirements and contact you within 24 hours to discuss your event details and provide a customized proposal.
            
            If you have any urgent questions, please don't hesitate to contact us directly.
            
            Best regards,
            The Event Planning Team
            
            This is an automated confirmation email. Please do not reply to this email.
            """
            
            # Create message
            message = Mail(
                from_email=From(self.from_email, "Event Planning Team"),
                to_emails=To(inquiry.email),
                subject=Subject(subject),
                html_content=HtmlContent(html_content),
                plain_text_content=PlainTextContent(plain_content)
            )
            
            # Send email
            sg = SendGridAPIClient(api_key=self.sendgrid_api_key)
            response = sg.send(message)
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"Customer confirmation email sent successfully for inquiry {inquiry.id}")
                return True, "Email sent successfully"
            else:
                logger.error(f"Failed to send customer email for inquiry {inquiry.id}. Status: {response.status_code}")
                return False, f"Failed to send email. Status: {response.status_code}"
                
        except Exception as e:
            logger.error(f"Error sending customer email for inquiry {inquiry.id}: {str(e)}")
            return False, f"Error sending email: {str(e)}"
    
    def send_both_notifications(self, inquiry):
        """Send both business and customer notifications"""
        business_success, business_message = self.send_business_email_notification(inquiry)
        customer_success, customer_message = self.send_customer_email_confirmation(inquiry)
        
        return {
            'business_email': {
                'success': business_success,
                'message': business_message
            },
            'customer_email': {
                'success': customer_success,
                'message': customer_message
            }
        }