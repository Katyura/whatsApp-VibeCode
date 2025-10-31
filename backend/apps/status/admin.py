from django.contrib import admin
from apps.status.models import StatusUpdate, StatusView

@admin.register(StatusUpdate)
class StatusUpdateAdmin(admin.ModelAdmin):
    list_display = ['user', 'status_type', 'visibility', 'created_at', 'expires_at']
    list_filter = ['status_type', 'visibility', 'created_at', 'expires_at']
    search_fields = ['user__phone_number', 'content']
    readonly_fields = ['id', 'created_at', 'expires_at']


@admin.register(StatusView)
class StatusViewAdmin(admin.ModelAdmin):
    list_display = ['status', 'viewer', 'viewed_at']
    search_fields = ['viewer__phone_number', 'status__user__phone_number']
    readonly_fields = ['id', 'viewed_at']
