import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from asgiref.sync import sync_to_async
import logging

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for 1-on-1 chats"""
    
    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.room_group_name = f'chat_{self.chat_id}'
        self.user = self.scope.get('user')
        
        # Verify token and authenticate
        if not self.user or not self.user.is_authenticated:
            await self.close()
            return
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        logger.info(f"User {self.user.phone_number} connected to chat {self.chat_id}")
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.info(f"User {self.user.phone_number} disconnected from chat {self.chat_id}")
    
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'text_message':
                await self.handle_text_message(data)
            elif message_type == 'typing':
                await self.handle_typing(data)
            elif message_type == 'read_receipt':
                await self.handle_read_receipt(data)
            elif message_type == 'message_edit':
                await self.handle_message_edit(data)
            elif message_type == 'message_delete':
                await self.handle_message_delete(data)
            elif message_type == 'reaction_add':
                await self.handle_reaction_add(data)
            elif message_type == 'reaction_remove':
                await self.handle_reaction_remove(data)
        except Exception as e:
            logger.error(f"Error in chat consumer: {str(e)}")
            await self.send(text_data=json.dumps({'error': 'Processing error'}))
    
    async def handle_text_message(self, data):
        content = data.get('content')
        message_type = data.get('message_type', 'TEXT')
        
        # Save message to database
        message = await self.save_message(content, message_type)
        
        # Broadcast to group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'text_message_received',
                'message_id': str(message.id),
                'sender_id': str(self.user.id),
                'sender_name': self.user.name,
                'content': message.content,
                'message_type': message.message_type,
                'created_at': message.created_at.isoformat(),
            }
        )
    
    async def handle_typing(self, data):
        is_typing = data.get('is_typing', False)
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'typing_indicator',
                'user_id': str(self.user.id),
                'user_name': self.user.name,
                'is_typing': is_typing,
            }
        )
    
    async def handle_read_receipt(self, data):
        message_id = data.get('message_id')
        
        # Save read receipt
        await self.save_read_receipt(message_id)
        
        # Broadcast read receipt
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'read_receipt_received',
                'message_id': message_id,
                'reader_id': str(self.user.id),
                'reader_name': self.user.name,
                'read_at': timezone.now().isoformat(),
            }
        )
    
    async def handle_message_edit(self, data):
        message_id = data.get('message_id')
        new_content = data.get('content')
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'message_edited',
                'message_id': message_id,
                'new_content': new_content,
                'edited_at': timezone.now().isoformat(),
            }
        )
    
    async def handle_message_delete(self, data):
        message_id = data.get('message_id')
        mode = data.get('mode', 'self_only')
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'message_deleted',
                'message_id': message_id,
                'mode': mode,
            }
        )
    
    async def handle_reaction_add(self, data):
        message_id = data.get('message_id')
        emoji = data.get('emoji')
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'reaction_added',
                'message_id': message_id,
                'user_id': str(self.user.id),
                'user_name': self.user.name,
                'emoji': emoji,
                'created_at': timezone.now().isoformat(),
            }
        )
    
    async def handle_reaction_remove(self, data):
        message_id = data.get('message_id')
        emoji = data.get('emoji')
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'reaction_removed',
                'message_id': message_id,
                'user_id': str(self.user.id),
                'emoji': emoji,
            }
        )
    
    # Event handlers (called by group_send)
    async def text_message_received(self, event):
        await self.send(text_data=json.dumps({
            'type': 'text_message_received',
            'message_id': event['message_id'],
            'sender_id': event['sender_id'],
            'sender_name': event['sender_name'],
            'content': event['content'],
            'message_type': event['message_type'],
            'created_at': event['created_at'],
        }))
    
    async def typing_indicator(self, event):
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'user_id': event['user_id'],
            'user_name': event['user_name'],
            'is_typing': event['is_typing'],
        }))
    
    async def read_receipt_received(self, event):
        await self.send(text_data=json.dumps({
            'type': 'read_receipt',
            'message_id': event['message_id'],
            'reader_id': event['reader_id'],
            'reader_name': event['reader_name'],
            'read_at': event['read_at'],
        }))
    
    async def message_edited(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message_edited',
            'message_id': event['message_id'],
            'new_content': event['new_content'],
            'edited_at': event['edited_at'],
        }))
    
    async def message_deleted(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message_deleted',
            'message_id': event['message_id'],
            'mode': event['mode'],
        }))
    
    async def reaction_added(self, event):
        await self.send(text_data=json.dumps({
            'type': 'reaction_added',
            'message_id': event['message_id'],
            'user_id': event['user_id'],
            'user_name': event['user_name'],
            'emoji': event['emoji'],
            'created_at': event['created_at'],
        }))
    
    async def reaction_removed(self, event):
        await self.send(text_data=json.dumps({
            'type': 'reaction_removed',
            'message_id': event['message_id'],
            'user_id': event['user_id'],
            'emoji': event['emoji'],
        }))
    
    @database_sync_to_async
    def save_message(self, content, message_type):
        from apps.messages.models import Message, Chat
        
        try:
            chat = Chat.objects.get(id=self.chat_id)
            message = Message.objects.create(
                chat=chat,
                sender=self.user,
                content=content,
                message_type=message_type
            )
            return message
        except Exception as e:
            logger.error(f"Error saving message: {str(e)}")
            return None
    
    @database_sync_to_async
    def save_read_receipt(self, message_id):
        from apps.messages.models import Message, ReadReceipt
        
        try:
            message = Message.objects.get(id=message_id)
            ReadReceipt.objects.get_or_create(
                message=message,
                user=self.user
            )
        except Exception as e:
            logger.error(f"Error saving read receipt: {str(e)}")


class GroupConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for group chats"""
    
    async def connect(self):
        self.group_id = self.scope['url_route']['kwargs']['group_id']
        self.room_group_name = f'group_{self.group_id}'
        self.user = self.scope.get('user')
        
        if not self.user or not self.user.is_authenticated:
            await self.close()
            return
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        logger.info(f"User {self.user.phone_number} connected to group {self.group_id}")
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'text_message':
                await self.handle_text_message(data)
            elif message_type == 'typing':
                await self.handle_typing(data)
            elif message_type == 'read_receipt':
                await self.handle_read_receipt(data)
        except Exception as e:
            logger.error(f"Error in group consumer: {str(e)}")
    
    async def handle_text_message(self, data):
        content = data.get('content')
        message_type = data.get('message_type', 'TEXT')
        
        message = await self.save_message(content, message_type)
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'text_message_received',
                'message_id': str(message.id),
                'sender_id': str(self.user.id),
                'sender_name': self.user.name,
                'content': message.content,
                'message_type': message.message_type,
                'created_at': message.created_at.isoformat(),
            }
        )
    
    async def handle_typing(self, data):
        is_typing = data.get('is_typing', False)
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'typing_indicator',
                'user_id': str(self.user.id),
                'user_name': self.user.name,
                'is_typing': is_typing,
            }
        )
    
    async def handle_read_receipt(self, data):
        message_id = data.get('message_id')
        await self.save_read_receipt(message_id)
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'read_receipt_received',
                'message_id': message_id,
                'reader_id': str(self.user.id),
                'read_at': timezone.now().isoformat(),
            }
        )
    
    async def text_message_received(self, event):
        await self.send(text_data=json.dumps(event))
    
    async def typing_indicator(self, event):
        await self.send(text_data=json.dumps(event))
    
    async def read_receipt_received(self, event):
        await self.send(text_data=json.dumps(event))
    
    @database_sync_to_async
    def save_message(self, content, message_type):
        from apps.messages.models import Message, Group
        
        try:
            group = Group.objects.get(id=self.group_id)
            message = Message.objects.create(
                group=group,
                sender=self.user,
                content=content,
                message_type=message_type
            )
            return message
        except Exception as e:
            logger.error(f"Error saving group message: {str(e)}")
            return None
    
    @database_sync_to_async
    def save_read_receipt(self, message_id):
        from apps.messages.models import Message, ReadReceipt
        
        try:
            message = Message.objects.get(id=message_id)
            ReadReceipt.objects.get_or_create(
                message=message,
                user=self.user
            )
        except Exception as e:
            logger.error(f"Error saving read receipt: {str(e)}")
