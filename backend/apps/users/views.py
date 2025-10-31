from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
import secrets

from apps.users.models import User, Device, OTPVerification, ContactList
from apps.users.serializers import (
    UserSerializer, DeviceSerializer, SendOTPSerializer, 
    VerifyOTPSerializer, ContactListSerializer, UpdateProfileSerializer
)
from utils.sms import generate_otp, send_otp_sms
from utils.encryption import hash_otp, verify_otp
from utils.jwt_auth import generate_token


class AuthViewSet(viewsets.ViewSet):
    """Authentication endpoints"""
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'], url_path='send-otp')
    def send_otp(self, request):
        """Send OTP to phone number"""
        serializer = SendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        phone_number = serializer.validated_data['phone_number']
        
        # Check rate limit - can resend after 30 seconds
        existing_otp = OTPVerification.objects.filter(
            phone_number=phone_number
        ).first()
        
        if existing_otp and not existing_otp.is_verified:
            time_diff = timezone.now() - (existing_otp.last_attempt_at or existing_otp.created_at)
            if time_diff.total_seconds() < 30:
                return Response(
                    {'error': 'Please wait 30 seconds before requesting a new OTP'},
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )
            
            # Check max attempts
            if existing_otp.attempts >= settings.OTP_MAX_ATTEMPTS:
                lockout_time = existing_otp.last_attempt_at + timedelta(minutes=settings.OTP_LOCKOUT_MINUTES)
                if timezone.now() < lockout_time:
                    return Response(
                        {'error': f'Too many attempts. Please try again after {lockout_time.strftime("%H:%M")}'},
                        status=status.HTTP_429_TOO_MANY_REQUESTS
                    )
            
            # Clear old OTP
            existing_otp.delete()
        
        # Generate OTP
        otp = generate_otp(settings.OTP_LENGTH)
        otp_hash = hash_otp(otp)
        
        # Create OTP record
        otp_record = OTPVerification.objects.create(
            phone_number=phone_number,
            otp_hash=otp_hash,
            expires_at=timezone.now() + timedelta(minutes=settings.OTP_VALIDITY_MINUTES)
        )
        
        # Send SMS
        send_otp_sms(phone_number, otp)
        
        return Response(
            {'message': 'OTP sent successfully'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['post'], url_path='verify-otp')
    def verify_otp(self, request):
        """Verify OTP and create/login user"""
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        phone_number = serializer.validated_data['phone_number']
        otp = serializer.validated_data['otp']
        device_id = serializer.validated_data['device_id']
        device_name = serializer.validated_data.get('device_name', 'Mobile Device')
        
        # Verify OTP
        otp_record = OTPVerification.objects.filter(
            phone_number=phone_number,
            is_verified=False
        ).first()
        
        if not otp_record:
            return Response(
                {'error': 'OTP not found or expired'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if timezone.now() > otp_record.expires_at:
            otp_record.delete()
            return Response(
                {'error': 'OTP expired'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not verify_otp(otp, otp_record.otp_hash):
            otp_record.attempts += 1
            otp_record.last_attempt_at = timezone.now()
            otp_record.save()
            
            if otp_record.attempts >= settings.OTP_MAX_ATTEMPTS:
                return Response(
                    {'error': 'Too many OTP attempts. Please request a new OTP.'},
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )
            
            return Response(
                {'error': 'Invalid OTP'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get or create user
        user, created = User.objects.get_or_create(phone_number=phone_number)
        if created:
            user.name = phone_number
            user.save()
        
        # Invalidate previous devices (single device login)
        Device.objects.filter(user=user, is_active=True).update(is_active=False)
        
        # Create new device
        session_token = secrets.token_urlsafe(32)
        device, _ = Device.objects.get_or_create(
            user=user,
            device_id=device_id,
            defaults={
                'device_name': device_name,
                'session_token': session_token,
                'is_active': True
            }
        )
        
        if not _.objects.get(device=device)[1]:  # If device exists
            device.session_token = session_token
            device.is_active = True
            device.save()
        
        # Generate JWT token
        access_token = generate_token(user.id, device_id)
        
        # Mark OTP as verified
        otp_record.is_verified = True
        otp_record.save()
        
        return Response(
            {
                'access_token': access_token,
                'user': UserSerializer(user).data,
                'device_id': device_id
            },
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['post'], url_path='logout')
    def logout(self, request):
        """Logout user and invalidate device"""
        user = request.user
        
        if hasattr(request, 'auth'):
            device_id = request.auth.get('device_id')
            Device.objects.filter(user=user, device_id=device_id).update(is_active=False)
        
        return Response(
            {'message': 'Logged out successfully'},
            status=status.HTTP_200_OK
        )


class UserViewSet(viewsets.ViewSet):
    """User profile endpoints"""
    permission_classes = [IsAuthenticated]
    
    def retrieve(self, request, pk=None):
        """Get user profile"""
        try:
            user = User.objects.get(id=pk)
            return Response(UserSerializer(user).data)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['put'], url_path='profile')
    def update_profile(self, request):
        """Update own profile"""
        serializer = UpdateProfileSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search users by phone number"""
        phone = request.query_params.get('phone')
        if not phone:
            return Response({'error': 'Phone parameter required'}, status=status.HTTP_400_BAD_REQUEST)
        
        users = User.objects.filter(phone_number__icontains=phone)[:10]
        return Response(UserSerializer(users, many=True).data)
