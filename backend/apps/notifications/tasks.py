"""Celery tasks for notifications"""
from celery import shared_task
from apps.notifications.models import Notification
from apps.messages.models import Message
from apps.users.models import Device
import firebase_admin
from firebase_admin import credentials, messaging
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_notification_to_device(device_id, title, body, data=None):
    """Send push notification to device via Firebase"""
    try:
        device = Device.objects.get(device_id=device_id, is_active=True)
        if device.fcm_token:
            message = messaging.Message(
                notification=messaging.Notification(title=title, body=body),
                data=data or {},
                token=device.fcm_token,
            )
            response = messaging.send(message)
            logger.info(f"Push notification sent: {response}")
            return response
    except Device.DoesNotExist:
        logger.warning(f"Device not found: {device_id}")
    except Exception as e:
        logger.error(f"Error sending push notification: {str(e)}")


@shared_task
def notify_offline_users_new_message(message_id):
    """Notify offline users when they receive a new message"""
    try:
        message = Message.objects.get(id=message_id)
        
        # Determine recipients
        if message.chat:
            if message.sender == message.chat.user1:
                recipient = message.chat.user2
            else:
                recipient = message.chat.user1
            recipients = [recipient]
        elif message.group:
            recipients = [
                m.user for m in message.group.members.filter(left_at__isnull=True)
                if m.user != message.sender
            ]
        else:
            return
        
        # Send to each offline recipient
        for recipient in recipients:
            active_device = Device.objects.filter(user=recipient, is_active=True).first()
            if active_device and active_device.fcm_token:
                # Check if user is online via WebSocket
                # This is simplified; in production, you'd check Redis for active connections
                title = message.sender.name
                if message.message_type == 'TEXT':
                    body = message.content[:50]
                else:
                    body = f"[{message.message_type}]"
                
                send_notification_to_device.delay(
                    active_device.device_id,
                    title,
                    body,
                    {"message_id": str(message_id), "type": "message"}
                )
    except Exception as e:
        logger.error(f"Error notifying users of new message: {str(e)}")


@shared_task
def notify_status_view(status_id, viewer_id):
    """Notify user when someone views their status"""
    try:
        from apps.status.models import StatusUpdate
        from apps.users.models import User
        
        status = StatusUpdate.objects.get(id=status_id)
        viewer = User.objects.get(id=viewer_id)
        
        device = Device.objects.filter(user=status.user, is_active=True).first()
        if device and device.fcm_token:
            send_notification_to_device.delay(
                device.device_id,
                f"{viewer.name} viewed your status",
                "",
                {"status_id": str(status_id), "type": "status_view"}
            )
    except Exception as e:
        logger.error(f"Error notifying status view: {str(e)}")


@shared_task
def notify_reaction(message_id, user_id, emoji):
    """Notify user when someone reacts to their message"""
    try:
        message = Message.objects.get(id=message_id)
        reacting_user = User.objects.get(id=user_id)
        
        if message.sender != reacting_user:
            device = Device.objects.filter(user=message.sender, is_active=True).first()
            if device and device.fcm_token:
                send_notification_to_device.delay(
                    device.device_id,
                    f"{reacting_user.name} reacted {emoji}",
                    "",
                    {"message_id": str(message_id), "type": "reaction"}
                )
    except Exception as e:
        logger.error(f"Error notifying reaction: {str(e)}")
