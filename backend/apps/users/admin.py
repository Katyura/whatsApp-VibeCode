from django.contrib import admin
from apps.users.models import User, Device, OTPVerification, ContactList

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['phone_number', 'name', 'is_active', 'last_seen', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['phone_number', 'name']
    readonly_fields = ['id', 'created_at', 'updated_at', 'last_seen']


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ['device_name', 'user', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['device_id', 'user__phone_number']
    readonly_fields = ['id', 'created_at', 'last_activity']


@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    list_display = ['phone_number', 'is_verified', 'attempts', 'created_at']
    list_filter = ['is_verified', 'created_at']
    search_fields = ['phone_number']
    readonly_fields = ['id', 'created_at', 'expires_at']


@admin.register(ContactList)
class ContactListAdmin(admin.ModelAdmin):
    list_display = ['contact_name', 'contact_phone', 'user', 'created_at']
    search_fields = ['user__phone_number', 'contact_phone', 'contact_name']
    readonly_fields = ['id', 'created_at']
