"""SMS utilities for OTP sending"""

import os
import random
from django.conf import settings
from twilio.rest import Client

def generate_otp(length=6):
    """Generate random OTP"""
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])


def send_otp_sms(phone_number, otp):
    """Send OTP via Twilio SMS"""
    try:
        account_sid = settings.TWILIO_ACCOUNT_SID
        auth_token = settings.TWILIO_AUTH_TOKEN
        twilio_phone = settings.TWILIO_PHONE_NUMBER
        
        if not all([account_sid, auth_token, twilio_phone]):
            # Development mode: just log the OTP
            print(f"[DEV] OTP for {phone_number}: {otp}")
            return True
        
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body=f"Your WhatsApp verification code is: {otp}. Valid for 5 minutes.",
            from_=twilio_phone,
            to=phone_number
        )
        return True
    except Exception as e:
        print(f"Error sending SMS: {str(e)}")
        return False


def send_notification_sms(phone_number, message):
    """Send notification SMS"""
    try:
        account_sid = settings.TWILIO_ACCOUNT_SID
        auth_token = settings.TWILIO_AUTH_TOKEN
        twilio_phone = settings.TWILIO_PHONE_NUMBER
        
        if not all([account_sid, auth_token, twilio_phone]):
            print(f"[DEV] SMS to {phone_number}: {message}")
            return True
        
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body=message,
            from_=twilio_phone,
            to=phone_number
        )
        return True
    except Exception as e:
        print(f"Error sending SMS: {str(e)}")
        return False
