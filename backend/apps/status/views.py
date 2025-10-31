from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta

from apps.status.models import StatusUpdate, StatusView
from apps.status.serializers import StatusUpdateSerializer, StatusViewSerializer, CreateStatusSerializer

class StatusViewSet(viewsets.ViewSet):
    """Status management endpoints"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'], url_path='feed')
    def get_feed(self, request):
        """Get status feed from contacts"""
        from apps.users.models import ContactList
        
        # Get user's contacts
        contacts = ContactList.objects.filter(user=request.user).values_list('contact_phone', flat=True)
        
        # Get statuses from contacts
        statuses = StatusUpdate.objects.filter(
            user__phone_number__in=contacts,
            expires_at__gt=timezone.now()
        ).order_by('-created_at')
        
        # Group by user
        status_feed = {}
        for st in statuses:
            if st.user.id not in status_feed:
                status_feed[st.user.id] = {
                    'user_id': str(st.user.id),
                    'user_name': st.user.name,
                    'statuses': [],
                    'unviewed_count': 0
                }
            
            status_feed[st.user.id]['statuses'].append(StatusUpdateSerializer(st).data)
            
            # Check if current user has viewed this status
            if not StatusView.objects.filter(status=st, viewer=request.user).exists():
                status_feed[st.user.id]['unviewed_count'] += 1
        
        return Response(list(status_feed.values()))
    
    @action(detail=False, methods=['post'], url_path='create')
    def create_status(self, request):
        """Create a new status"""
        serializer = CreateStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        content = serializer.validated_data['content']
        status_type = serializer.validated_data['status_type']
        visibility = serializer.validated_data['visibility']
        visible_to_ids = serializer.validated_data.get('visible_to_ids', [])
        
        status_update = StatusUpdate.objects.create(
            user=request.user,
            content=content,
            status_type=status_type,
            visibility=visibility,
            visible_to_ids=visible_to_ids if visibility == 'SPECIFIC_USERS' else [],
            expires_at=timezone.now() + timedelta(hours=24)
        )
        
        return Response(
            StatusUpdateSerializer(status_update).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail='', methods=['get'])
    def get_status(self, request, pk=None):
        """Get single status with viewers"""
        try:
            status_update = StatusUpdate.objects.get(id=pk)
            
            # Check visibility
            if status_update.visibility == 'SPECIFIC_USERS':
                if str(request.user.id) not in status_update.visible_to_ids and request.user != status_update.user:
                    return Response(
                        {'error': 'You do not have access to this status'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            
            views = StatusView.objects.filter(status=status_update)
            return Response({
                'status': StatusUpdateSerializer(status_update).data,
                'viewers': StatusViewSerializer(views, many=True).data
            })
        except StatusUpdate.DoesNotExist:
            return Response({'error': 'Status not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['post'], url_path='view')
    def record_view(self, request):
        """Record view of a status"""
        status_id = request.data.get('status_id')
        
        try:
            status_update = StatusUpdate.objects.get(id=status_id)
            
            # Check visibility
            if status_update.visibility == 'SPECIFIC_USERS':
                if str(request.user.id) not in status_update.visible_to_ids:
                    return Response(
                        {'error': 'You do not have access to this status'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            
            view, created = StatusView.objects.get_or_create(
                status=status_update,
                viewer=request.user
            )
            
            return Response(
                {'message': 'View recorded'},
                status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
            )
        except StatusUpdate.DoesNotExist:
            return Response({'error': 'Status not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['delete'])
    def delete_status(self, request):
        """Delete own status"""
        status_id = request.data.get('status_id')
        
        try:
            status_update = StatusUpdate.objects.get(id=status_id)
            
            if status_update.user != request.user:
                return Response(
                    {'error': 'You can only delete your own statuses'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            status_update.delete()
            return Response({'message': 'Status deleted'})
        except StatusUpdate.DoesNotExist:
            return Response({'error': 'Status not found'}, status=status.HTTP_404_NOT_FOUND)
