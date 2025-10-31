import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(models.Model):
    """Custom User model with phone-based authentication"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(max_length=20, unique=True, db_index=True)
    name = models.CharField(max_length=255, blank=True)
    bio = models.TextField(blank=True, null=True)
    status_message = models.CharField(max_length=255, blank=True, null=True)
    profile_picture_url = models.CharField(max_length=500, blank=True, null=True)
    last_seen = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-last_seen']
        indexes = [
            models.Index(fields=['phone_number']),
            models.Index(fields=['-last_seen']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.phone_number})"


class Device(models.Model):
    """Track devices for single-device login enforcement"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='devices')
    device_id = models.CharField(max_length=255, unique=True, db_index=True)
    device_name = models.CharField(max_length=255, blank=True)
    session_token = models.CharField(max_length=500, unique=True)
    fcm_token = models.CharField(max_length=500, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'is_active'],
                condition=models.Q(is_active=True),
                name='unique_active_device_per_user'
            )
        ]
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['device_id']),
        ]
    
    def __str__(self):
        return f"{self.device_name} ({self.user.phone_number})"


class OTPVerification(models.Model):
    """OTP verification records for authentication"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(max_length=20, db_index=True)
    otp_hash = models.CharField(max_length=255)
    attempts = models.IntegerField(default=0)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    last_attempt_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['phone_number', 'expires_at']),
        ]
    
    def __str__(self):
        return f"OTP for {self.phone_number}"


class ContactList(models.Model):
    """User's saved contacts"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contacts')
    contact_phone = models.CharField(max_length=20)
    contact_name = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'contact_phone')
        indexes = [
            models.Index(fields=['user', 'contact_phone']),
        ]
    
    def __str__(self):
        return f"{self.contact_name} ({self.contact_phone})"
