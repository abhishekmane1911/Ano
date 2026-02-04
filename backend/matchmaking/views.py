from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Exists, OuterRef
from django.shortcuts import get_object_or_404

from .models import Swipe, Match
from profiles.models import Profile
from chat.models import Message
from .serializers import SwipeSerializer, MatchSerializer, MatchMessageSerializer
from profiles.serializers import ProfileSerializer
from reports.utils import filter_blocked_profiles


class MatchmakingViewSet(viewsets.ViewSet):
    """ViewSet for matchmaking operations"""
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'], url_path='profiles')
    def get_profiles_for_swiping(self, request):
        """
        Get profiles for swiping, excluding:
        - Own profile
        - Already swiped profiles
        - Blocked users
        """
        user_profile = request.user.profile
        
        # Get IDs of profiles already swiped on
        swiped_profile_ids = Swipe.objects.filter(
            swiper=user_profile
        ).values_list('swiped_id', flat=True)
        
        # Get profiles excluding own profile and already swiped
        profiles = Profile.objects.exclude(
            id=user_profile.id
        ).exclude(
            id__in=swiped_profile_ids
        )
        
        # Exclude blocked users
        profiles = filter_blocked_profiles(profiles, user_profile)
        
        serializer = ProfileSerializer(profiles, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], url_path='swipe')
    def record_swipe(self, request):
        """
        Record a swipe (left or right) and check for mutual match
        """
        user_profile = request.user.profile
        
        # Add swiper to the data
        data = request.data.copy()
        data['swiper'] = user_profile.id
        
        serializer = SwipeSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            swipe = serializer.save(swiper=user_profile)
            
            # If swipe is right, check for mutual match
            if swipe.direction == 'right':
                # Check if the other user also swiped right
                mutual_swipe = Swipe.objects.filter(
                    swiper=swipe.swiped,
                    swiped=user_profile,
                    direction='right'
                ).first()
                
                if mutual_swipe:
                    # Create a match
                    match = Match.objects.create(
                        profile1=user_profile,
                        profile2=swipe.swiped
                    )
                    match_serializer = MatchSerializer(match, context={'request': request})
                    return Response({
                        'swipe': serializer.data,
                        'match': match_serializer.data,
                        'is_match': True
                    }, status=status.HTTP_201_CREATED)
            
            return Response({
                'swipe': serializer.data,
                'is_match': False
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], url_path='matches')
    def list_matches(self, request):
        """Get all matches for the current user"""
        user_profile = request.user.profile
        
        matches = Match.objects.filter(
            Q(profile1=user_profile) | Q(profile2=user_profile),
            is_active=True
        )
        
        serializer = MatchSerializer(matches, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], url_path='detail')
    def match_detail(self, request, pk=None):
        """Get details of a specific match"""
        user_profile = request.user.profile
        
        match = get_object_or_404(
            Match,
            pk=pk,
            is_active=True
        )
        
        # Verify user is part of the match
        if not match.has_profile(user_profile):
            return Response(
                {'error': 'You are not part of this match'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = MatchSerializer(match, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], url_path='messages')
    def match_messages(self, request, pk=None):
        """Get messages for a specific match with pagination"""
        user_profile = request.user.profile
        
        match = get_object_or_404(
            Match,
            pk=pk,
            is_active=True
        )
        
        # Verify user is part of the match
        if not match.has_profile(user_profile):
            return Response(
                {'error': 'You are not part of this match'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get messages for this match
        messages = Message.objects.filter(
            match=match,
            is_deleted=False
        ).select_related('sender').order_by('created_at')
        
        # Paginate
        page = self.paginate_queryset(messages)
        if page is not None:
            serializer = MatchMessageSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = MatchMessageSerializer(messages, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='messages/send')
    def send_match_message(self, request, pk=None):
        """Send a message in a match chat"""
        user_profile = request.user.profile
        
        match = get_object_or_404(
            Match,
            pk=pk,
            is_active=True
        )
        
        # Verify user is part of the match
        if not match.has_profile(user_profile):
            return Response(
                {'error': 'You are not part of this match'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Add match and sender to the data
        data = request.data.copy()
        data['match'] = match.id
        data['sender'] = user_profile.id
        
        serializer = MatchMessageSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            message = serializer.save(
                match=match,
                sender=user_profile
            )
            return Response(
                MatchMessageSerializer(message, context={'request': request}).data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], url_path='messages/upload')
    def upload_match_media(self, request, pk=None):
        """Upload media file for match chat"""
        user_profile = request.user.profile
        
        match = get_object_or_404(
            Match,
            pk=pk,
            is_active=True
        )
        
        # Verify user is part of the match
        if not match.has_profile(user_profile):
            return Response(
                {'error': 'You are not part of this match'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Rate limiting for file uploads (max 10 uploads per hour per user)
        from django.core.cache import cache
        cache_key = f'file_upload_rate_limit_{request.user.id}'
        upload_count = cache.get(cache_key, 0)
        
        if upload_count >= 10:
            return Response(
                {'error': 'Upload rate limit exceeded. Please try again later.'},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        
        if 'file' not in request.FILES:
            return Response(
                {'error': 'No file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        file = request.FILES['file']
        
        # File validation
        from ano_backend.file_validators import validate_uploaded_file
        from django.core.exceptions import ValidationError as DjangoValidationError
        
        try:
            validate_uploaded_file(file, file_type='image')
        except DjangoValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Compress and save image
        try:
            from PIL import Image
            import io
            import os
            from django.conf import settings
            import re
            
            # Sanitize filename - remove path separators and dangerous characters
            safe_name = re.sub(r'[^\w\-_\.]', '_', file.name)
            safe_name = safe_name[:100]  # Limit length
            if not safe_name:
                safe_name = 'image.jpg'
            
            img = Image.open(file)
            
            # Verify it's actually an image and not malicious content
            img.verify()
            
            # Reopen for processing (verify() closes the image)
            file.seek(0)
            img = Image.open(file)
            
            # Convert RGBA to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Resize if larger than max_size
            img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
            
            # Save to bytes
            output = io.BytesIO()
            img.save(output, format='JPEG', quality=85, optimize=True)
            
            # Check processed file size
            processed_size = len(output.getvalue())
            if processed_size > 5 * 1024 * 1024:  # 5MB limit for processed files
                return Response(
                    {'error': 'Processed image is too large'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Save to media directory
            media_path = os.path.join(settings.MEDIA_ROOT, 'match_media')
            os.makedirs(media_path, exist_ok=True)
            
            import uuid
            # Generate secure filename
            file_name = f"{uuid.uuid4().hex}_{safe_name}"
            file_path = os.path.join(media_path, file_name)
            
            # Ensure file doesn't already exist (extremely unlikely but safe)
            counter = 1
            while os.path.exists(file_path):
                name_parts = safe_name.rsplit('.', 1)
                if len(name_parts) == 2:
                    new_name = f"{name_parts[0]}_{counter}.{name_parts[1]}"
                else:
                    new_name = f"{safe_name}_{counter}"
                file_name = f"{uuid.uuid4().hex}_{new_name}"
                file_path = os.path.join(media_path, file_name)
                counter += 1
                if counter > 100:  # Prevent infinite loop
                    break
            
            # Write file atomically
            temp_path = f"{file_path}.tmp"
            try:
                with open(temp_path, 'wb') as f:
                    f.write(output.getvalue())
                os.rename(temp_path, file_path)
            except Exception as e:
                # Clean up temp file if it exists
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                raise e
            
            # Return absolute media URL
            # Build absolute URL for the media file
            request_scheme = 'https' if request.is_secure() else 'http'
            request_host = request.get_host()
            media_url = f"{request_scheme}://{request_host}{settings.MEDIA_URL}match_media/{file_name}"
            
            # Increment upload counter for rate limiting
            cache.set(cache_key, upload_count + 1, 3600)  # 1 hour timeout
            
            return Response({'media_url': media_url}, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to process image: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    # Pagination methods
    @property
    def paginator(self):
        if not hasattr(self, '_paginator'):
            from rest_framework.pagination import PageNumberPagination
            self._paginator = PageNumberPagination()
            self._paginator.page_size = 50
        return self._paginator
    
    def paginate_queryset(self, queryset):
        return self.paginator.paginate_queryset(queryset, self.request, view=self)
    
    def get_paginated_response(self, data):
        return self.paginator.get_paginated_response(data)
