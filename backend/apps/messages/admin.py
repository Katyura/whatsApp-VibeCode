from django.contrib import admin
from apps.messages.models import Chat, Group, GroupMember, Message, MessageReaction, ReadReceipt

@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ['user1', 'user2', 'created_at', 'updated_at']
    search_fields = ['user1__phone_number', 'user2__phone_number']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'created_at', 'updated_at']
    search_fields = ['name', 'created_by__phone_number']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(GroupMember)
class GroupMemberAdmin(admin.ModelAdmin):
    list_display = ['group', 'user', 'is_admin', 'joined_at']
    list_filter = ['is_admin', 'joined_at']
    search_fields = ['group__name', 'user__phone_number']
    readonly_fields = ['id', 'joined_at']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'message_type', 'is_deleted', 'created_at']
    list_filter = ['message_type', 'is_deleted', 'created_at']
    search_fields = ['sender__phone_number', 'content']
    readonly_fields = ['id', 'created_at']


@admin.register(MessageReaction)
class MessageReactionAdmin(admin.ModelAdmin):
    list_display = ['message', 'user', 'emoji', 'created_at']
    search_fields = ['user__phone_number', 'emoji']
    readonly_fields = ['id', 'created_at']


@admin.register(ReadReceipt)
class ReadReceiptAdmin(admin.ModelAdmin):
    list_display = ['message', 'user', 'read_at']
    search_fields = ['user__phone_number', 'message__id']
    readonly_fields = ['id', 'read_at']
