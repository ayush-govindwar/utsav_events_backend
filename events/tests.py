import os
import django
import requests
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'events_backend.settings')
django.setup()

from django.conf import settings

def verify_whatsapp_setup():
    """Verify WhatsApp configuration and test with correct phone numbers"""
    
    print("=== WhatsApp Setup Verification ===")
    
    access_token = settings.WHATSAPP_ACCESS_TOKEN
    phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID
    business_phone = settings.BUSINESS_PHONE_NUMBER
    
    print(f"Phone Number ID: {phone_number_id}")
    print(f"Business Phone: {business_phone}")
    print(f"Access Token: {'*' * 10 + access_token[-10:] if access_token else 'NOT SET'}")
    
    # Test phone numbers - UPDATE THESE WITH YOUR ACTUAL TEST NUMBERS
    test_numbers = [
        "15551234567",    # US format - replace with your actual test number
        "919876543210",   # Indian format - if you have Indian test recipients
    ]
    
    url = f"https://graph.facebook.com/v18.0/{phone_number_id}/messages"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    for test_phone in test_numbers:
        print(f"\n--- Testing phone number: {test_phone} ---")
        
        payload = {
            "messaging_product": "whatsapp",
            "to": test_phone,
            "type": "text",
            "text": {
                "body": f"Test message to {test_phone} from Django backend! 🚀"
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            print(f"Status Code: {response.status_code}")
            
            try:
                response_json = response.json()
                print(f"Response: {json.dumps(response_json, indent=2)}")
                
                if response.status_code == 200:
                    print("✅ SUCCESS: Message sent!")
                else:
                    print("❌ FAILED: Check error details above")
                    
                    # Common error explanations
                    if 'error' in response_json:
                        error = response_json['error']
                        if error.get('code') == 131026:
                            print("💡 This phone number is not a valid WhatsApp number or not in test recipients")
                        elif error.get('code') == 131047:
                            print("💡 This phone number is not verified for testing")
                        elif error.get('code') == 131031:
                            print("💡 Phone number format is incorrect")
                        
            except:
                print(f"Response Text: {response.text}")
                
        except Exception as e:
            print(f"Request Error: {e}")

def test_business_phone_format():
    """Test different formats for business phone"""
    
    print("\n=== Testing Business Phone Formats ===")
    
    # If your business phone is a US number like +1-555-123-4567
    # Try these formats:
    business_formats = [
        "15551234567",     # Recommended for US numbers
        "+15551234567",    # With plus sign
        "1551234567",      # Sometimes works
    ]
    
    access_token = settings.WHATSAPP_ACCESS_TOKEN
    phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID
    
    url = f"https://graph.facebook.com/v18.0/{phone_number_id}/messages"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    for business_phone in business_formats:
        print(f"\nTesting business phone format: {business_phone}")
        
        payload = {
            "messaging_product": "whatsapp",
            "to": business_phone,
            "type": "text",
            "text": {
                "body": "Test business notification message! 📋"
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ This format works!")
                print(f"💡 Update your .env file: BUSINESS_PHONE_NUMBER={business_phone}")
            else:
                try:
                    error_details = response.json()
                    print(f"❌ Failed: {json.dumps(error_details, indent=2)}")
                except:
                    print(f"❌ Failed: {response.text}")
                    
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    print("🚨 IMPORTANT: Update the test phone numbers in this script!")
    print("Replace the test_numbers with your actual WhatsApp test recipients")
    print("=" * 60)
    
    verify_whatsapp_setup()
    test_business_phone_format()
    
    print("\n" + "=" * 60)
    print("Next steps:")
    print("1. Add your phone numbers to WhatsApp test recipients in Meta Business Manager")
    print("2. Use the correct format that worked in the tests above")
    print("3. Update your .env file with the working phone number format")
    print("4. Test your Django API again")