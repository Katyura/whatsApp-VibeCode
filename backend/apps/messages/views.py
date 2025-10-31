from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta

from apps.messages.models import Chat, Group, GroupMember, Message, MessageReaction, ReadReceipt
from apps.messages.serializers import (
    ChatSerializer, GroupSerializer, MessageSerializer, 
    CreateMessageSerializer, MessageReactionSerializer
)
from apps.users.models import User


class ChatViewSet(viewsets.ModelViewSet):
    """Chat management endpoints"""
    serializer_class = ChatSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get chats for current user"""
        user = self.request.user
        return Chat.objects.filter(user1=user) | Chat.objects.filter(user2=user)
    
    def create(self, request):
        """Create a new chat with a user"""
        other_user_id = request.data.get('user_id')
        
        try:
            other_user = User.objects.get(id=other_user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if other_user == request.user:
            return Response({'error': 'Cannot chat with yourself'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create or get chat
        user1 = request.user if request.user.id < other_user.id else other_user
        user2 = other_user if request.user.id < other_user.id else request.user
        
        chat, created = Chat.objects.get_or_create(user1=user1, user2=user2)
        return Response(ChatSerializer(chat).data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """Get messages in a chat"""
        chat = self.get_object()
        page = int(request.query_params.get('page', 0))
        limit = int(request.query_params.get('limit', 50))
        
        messages = Message.objects.filter(chat=chat).order_by('-created_at')[page*limit:(page+1)*limit]
        return Response(MessageSerializer(messages, many=True).data)


class GroupViewSet(viewsets.ModelViewSet):
    """Group management endpoints"""
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get groups for current user"""
        user = self.request.user
        return Group.objects.filter(members__user=user, members__left_at__isnull=True).distinct()
    
    def create(self, request):
        """Create a new group"""
        name = request.data.get('name')
        member_ids = request.data.get('members', [])
        description = request.data.get('description', '')
        
        if not name:
            return Response({'error': 'Group name required'}, status=status.HTTP_400_BAD_REQUEST)
        
        group = Group.objects.create(
            name=name,
            description=description,
            created_by=request.user
        )
        
        # Add creator as admin
        GroupMember.objects.create(group=group, user=request.user, is_admin=True)
        
        # Add other members
        for member_id in member_ids:
            try:
                user = User.objects.get(id=member_id)
                GroupMember.objects.create(group=group, user=user)
            except User.DoesNotExist:
                pass
        
        return Response(GroupSerializer(group).data, status=status.HTTP_201_CREATED)
    
    def update(self, request, pk=None):
        """Update group (admin only)"""
        group = self.get_object()
        
        # Check if user is admin
        if not GroupMember.objects.filter(group=group, user=request.user, is_admin=True).exists():
            return Response({'error': 'Insufficient permissions'}, status=status.HTTP_403_FORBIDDEN)
        
        name = request.data.get('name')
        description = request.data.get('description')
        picture_url = request.data.get('group_picture_url')
        
        if name:
            group.name = name
        if description:
            group.description = description
        if picture_url:
            group.group_picture_url = picture_url
        
        group.save()
        return Response(GroupSerializer(group).data)
    
    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        """Add member to group (admin only)"""
        group = self.get_object()
        
        if not GroupMember.objects.filter(group=group, user=request.user, is_admin=True).exists():
            return Response({'error': 'Insufficient permissions'}, status=status.HTTP_403_FORBIDDEN)
        
        user_id = request.data.get('user_id')
        try:
            user = User.objects.get(id=user_id)
            member, created = GroupMember.objects.get_or_create(group=group, user=user)
            return Response(status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def remove_member(self, request, pk=None):
        """Remove member from group (admin only)"""
        group = self.get_object()
        
        if not GroupMember.objects.filter(group=group, user=request.user, is_admin=True).exists():
            return Response({'error': 'Insufficient permissions'}, status=status.HTTP_403_FORBIDDEN)
        
        user_id = request.data.get('user_id')
        GroupMember.objects.filter(group=group, user_id=user_id).update(left_at=timezone.now())
        return Response(status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        """Leave group"""
        group = self.get_object()
        GroupMember.objects.filter(group=group, user=request.user).update(left_at=timezone.now())
        return Response(status=status.HTTP_200_OK)


class MessageViewSet(viewsets.ViewSet):
    """Message endpoints"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'], url_path='send')
    def send_message(self, request):
        """Send a message (usually via WebSocket, but API fallback)"""
        serializer = CreateMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        chat_type = serializer.validated_data['chat_type']
        content = serializer.validated_data['content']
        message_type = serializer.validated_data['message_type']
        
        if chat_type == 'chat':
            chat_id = serializer.validated_data['chat_id']
            try:
                chat = Chat.objects.get(id=chat_id)
                message = Message.objects.create(
                    chat=chat,
                    sender=request.user,
                    content=content,
                    message_type=message_type
                )
                return Response(MessageSerializer(message).data, status=status.HTTP_201_CREATED)
            except Chat.DoesNotExist:
                return Response({'error': 'Chat not found'}, status=status.HTTP_404_NOT_FOUND)
        
        elif chat_type == 'group':
            group_id = serializer.validated_data['group_id']
            try:
                group = Group.objects.get(id=group_id)
                message = Message.objects.create(
                    group=group,
                    sender=request.user,
                    content=content,
                    message_type=message_type
                )
                return Response(MessageSerializer(message).data, status=status.HTTP_201_CREATED)
            except Group.DoesNotExist:
                return Response({'error': 'Group not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['patch'], url_path='edit')
    def edit_message(self, request):
        """Edit a message"""
        message_id = request.data.get('message_id')
        new_content = request.data.get('content')
        
        try:
            message = Message.objects.get(id=message_id)
            
            if message.sender != request.user:
                return Response({'error': 'Can only edit your own messages'}, status=status.HTTP_403_FORBIDDEN)
            
            # Check if message is < 15 minutes old
            time_diff = timezone.now() - message.created_at
            if time_diff.total_seconds() > 15 * 60:
                return Response({'error': 'Message can only be edited within 15 minutes'}, status=status.HTTP_400_BAD_REQUEST)
            
            message.content = new_content
            message.edited_at = timezone.now()
            message.save()
            
            return Response(MessageSerializer(message).data)
        except Message.DoesNotExist:
            return Response({'error': 'Message not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['post'], url_path='react')
    def add_reaction(self, request):
        """Add reaction to message"""
        message_id = request.data.get('message_id')
        emoji = request.data.get('emoji')
        
        try:
            message = Message.objects.get(id=message_id)
            reaction, created = MessageReaction.objects.get_or_create(
                message=message,
                user=request.user,
                emoji=emoji
            )
            return Response(MessageReactionSerializer(reaction).data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
        except Message.DoesNotExist:
            return Response({'error': 'Message not found'}, status=status.HTTP_404_NOT_FOUND)
