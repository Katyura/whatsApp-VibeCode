import uuid
from django.db import models
from apps.users.models import User

class Notification(models.Model):
    """Notification records for push notifications"""
    NOTIFICATION_TYPES = [
        ('MESSAGE', 'New Message'),
        ('GROUP_MESSAGE', 'Group Message'),
        ('STATUS', 'New Status'),
        ('REACTION', 'Message Reaction'),
        ('GROUP_INVITE', 'Group Invite'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    body = models.TextField()
    related_object_id = models.UUIDField(null=True, blank=True)
    related_object_type = models.CharField(max_length=50, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'is_read']),
        ]
    
    def __str__(self):
        return f"Notification for {self.user.phone_number}: {self.title}"
