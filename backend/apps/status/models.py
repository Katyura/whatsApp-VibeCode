import uuid
from django.db import models
from django.contrib.postgres.fields import ArrayField
from apps.users.models import User

class StatusUpdate(models.Model):
    """Status updates (24-hour stories)"""
    STATUS_TYPES = [
        ('TEXT', 'Text'),
        ('IMAGE', 'Image'),
        ('VIDEO', 'Video'),
    ]
    
    VISIBILITY_CHOICES = [
        ('EVERYONE', 'Everyone'),
        ('CONTACTS_ONLY', 'Contacts Only'),
        ('SPECIFIC_USERS', 'Specific Users'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='statuses')
    content = models.TextField()
    status_type = models.CharField(max_length=20, choices=STATUS_TYPES, default='TEXT')
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='EVERYONE')
    visible_to_ids = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"Status from {self.user.phone_number} at {self.created_at}"


class StatusView(models.Model):
    """Status view tracking"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status = models.ForeignKey(StatusUpdate, on_delete=models.CASCADE, related_name='views')
    viewer = models.ForeignKey(User, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('status', 'viewer')
        indexes = [
            models.Index(fields=['status', 'viewer']),
            models.Index(fields=['status', '-viewed_at']),
        ]
    
    def __str__(self):
        return f"{self.viewer.phone_number} viewed status {self.status.id}"
