from rest_framework import serializers
from apps.status.models import StatusUpdate, StatusView

class StatusViewSerializer(serializers.ModelSerializer):
    viewer_name = serializers.CharField(source='viewer.name', read_only=True)
    
    class Meta:
        model = StatusView
        fields = ['id', 'viewer', 'viewer_name', 'viewed_at']
        read_only_fields = ['id', 'viewed_at']


class StatusUpdateSerializer(serializers.ModelSerializer):
    views = StatusViewSerializer(many=True, read_only=True)
    user_name = serializers.CharField(source='user.name', read_only=True)
    
    class Meta:
        model = StatusUpdate
        fields = ['id', 'user', 'user_name', 'content', 'status_type', 'visibility', 
                  'visible_to_ids', 'views', 'created_at', 'expires_at']
        read_only_fields = ['id', 'created_at', 'expires_at', 'views']


class CreateStatusSerializer(serializers.Serializer):
    content = serializers.CharField(max_length=5000)
    status_type = serializers.ChoiceField(choices=['TEXT', 'IMAGE', 'VIDEO'])
    visibility = serializers.ChoiceField(choices=['EVERYONE', 'CONTACTS_ONLY', 'SPECIFIC_USERS'])
    visible_to_ids = serializers.ListField(child=serializers.UUIDField(), required=False)
