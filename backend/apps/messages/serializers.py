from rest_framework import serializers
from apps.messages.models import Chat, Group, GroupMember, Message, MessageReaction, ReadReceipt

class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = ['id', 'user1', 'user2', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class GroupSerializer(serializers.ModelSerializer):
    members = serializers.SerializerMethodField()
    
    def get_members(self, obj):
        members = obj.members.filter(left_at__isnull=True)
        return GroupMemberSerializer(members, many=True).data
    
    class Meta:
        model = Group
        fields = ['id', 'name', 'group_picture_url', 'description', 'created_by', 'members', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']


class GroupMemberSerializer(serializers.ModelSerializer):
    user_details = serializers.SerializerMethodField()
    
    def get_user_details(self, obj):
        from apps.users.serializers import UserSerializer
        return UserSerializer(obj.user).data
    
    class Meta:
        model = GroupMember
        fields = ['id', 'user', 'user_details', 'is_admin', 'joined_at', 'left_at']
        read_only_fields = ['id', 'joined_at']


class MessageReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageReaction
        fields = ['id', 'user', 'emoji', 'created_at']
        read_only_fields = ['id', 'created_at']


class ReadReceiptSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReadReceipt
        fields = ['id', 'user', 'read_at']
        read_only_fields = ['id', 'read_at']


class MessageSerializer(serializers.ModelSerializer):
    reactions = MessageReactionSerializer(many=True, read_only=True)
    read_receipts = ReadReceiptSerializer(many=True, read_only=True)
    sender_name = serializers.CharField(source='sender.name', read_only=True)
    
    class Meta:
        model = Message
        fields = ['id', 'chat', 'group', 'sender', 'sender_name', 'content', 'message_type', 
                  'is_deleted', 'deleted_by_sender_only', 'forwarded_from', 'edited_at', 
                  'created_at', 'reactions', 'read_receipts']
        read_only_fields = ['id', 'sender', 'created_at', 'read_receipts']


class CreateMessageSerializer(serializers.Serializer):
    chat_type = serializers.ChoiceField(choices=['chat', 'group'])
    chat_id = serializers.UUIDField(required=False, allow_null=True)
    group_id = serializers.UUIDField(required=False, allow_null=True)
    content = serializers.CharField(max_length=5000)
    message_type = serializers.ChoiceField(choices=['TEXT', 'IMAGE', 'VIDEO', 'FILE', 'AUDIO'])
