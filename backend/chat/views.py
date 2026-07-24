from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.contrib.postgres.search import SearchQuery, SearchRank
from django.db.models import Q
from PIL import Image
import io
import os
from django.conf import settings
from rest_framework.throttling import ScopedRateThrottle

# Import privilege enforcement decorators
from reputation.services import require_privilege_drf

from .models import Chatroom, Message, MessageReaction, ReadReceipt, Poll, PollVote, Confession
from .serializers import (
    ChatroomSerializer,
    MessageSerializer,
    MessageCreateSerializer,
    MessageUpdateSerializer,
    ReactionCreateSerializer,
    MessageReactionSerializer,
    ReadReceiptSerializer,
    MessageSearchResultSerializer,
    PollSerializer,
    PollCreateSerializer,
    PollVoteSerializer,
    ConfessionSerializer,
    ConfessionCreateSerializer
)
from matchmaking.models import Match


class MessagePagination(PageNumberPagination):
    """Pagination for messages with infinite scroll support"""
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100


class ChatroomViewSet(viewsets.ModelViewSet):
    """ViewSet for Chatroom operations"""
    
    queryset = Chatroom.objects.filter(is_active=True)
    serializer_class = ChatroomSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = None
    
    def list(self, request):
        """List all active chatrooms"""
        chatrooms = self.get_queryset()
        serializer = self.get_serializer(chatrooms, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):
        """Get chatroom details"""
        chatroom = get_object_or_404(Chatroom, pk=pk, is_active=True)
        serializer = self.get_serializer(chatroom)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """Get paginated messages for a chatroom"""
        chatroom = get_object_or_404(Chatroom, pk=pk, is_active=True)
        
        # Get ordering parameter
        ordering = request.query_params.get('ordering', 'created_at')
        
        # Base queryset
        messages = Message.objects.filter(
            chatroom=chatroom,
            is_deleted=False
        ).select_related('sender').prefetch_related(
            'reactions',
            'ranking',
        )
        
        # Apply ordering based on parameter
        if ordering == 'wilson_score':
            # Order by Wilson Score (highest first)
            try:
                from reputation.models import MessageRanking
                messages = messages.select_related('ranking').order_by('-ranking__wilson_score', '-created_at')
            except ImportError:
                # Fallback to created_at if reputation app not available
                messages = messages.order_by('-created_at')
        elif ordering == 'upvotes':
            # Order by upvote count
            try:
                from reputation.models import MessageRanking
                messages = messages.select_related('ranking').order_by('-ranking__upvotes', '-created_at')
            except ImportError:
                messages = messages.order_by('-created_at')
        elif ordering == 'controversial':
            # Order by most controversial (high total votes, low Wilson Score)
            try:
                from reputation.models import MessageRanking
                from django.db.models import F
                messages = messages.select_related('ranking').annotate(
                    total_votes=F('ranking__upvotes') + F('ranking__downvotes')
                ).filter(total_votes__gt=5).order_by('ranking__wilson_score', '-total_votes')
            except ImportError:
                messages = messages.order_by('-created_at')
        else:
            messages = messages.order_by('-created_at')
        
        paginator = MessagePagination()
        page = paginator.paginate_queryset(messages, request)
        
        if page is not None:
            serializer = MessageSerializer(page, many=True, context={'request': request})
            return paginator.get_paginated_response(serializer.data)
        
        serializer = MessageSerializer(messages, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """Send a message to a chatroom"""
        chatroom = get_object_or_404(Chatroom, pk=pk, is_active=True)
        
       
        try:
            profile = request.user.profile
        except:
            return Response(
                {'error': 'Profile not found. Please create a profile first.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = MessageCreateSerializer(data=request.data)
        if serializer.is_valid():
            message = serializer.save(
                chatroom=chatroom,
                sender=profile
            )
            response_serializer = MessageSerializer(message)
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @require_privilege_drf('upload_images')
    @action(detail=True, methods=['post'], url_path='upload_media', throttle_scope='chatroom_media_upload')
    def upload_media(self, request, pk=None):
        """Upload media file for chatroom"""
        chatroom = get_object_or_404(Chatroom, pk=pk, is_active=True)
        
        try:
            profile = request.user.profile
        except:
            return Response(
                {'error': 'Profile not found.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Rate limiting for file uploads (max 10 uploads per hour per user)
        # from django.core.cache import cache
        # cache_key = f'file_upload_rate_limit_{request.user.id}'
        # upload_count = cache.get(cache_key, 0)
        
        # if upload_count >= 10:
        #     return Response(
        #         {'error': 'Upload rate limit exceeded. Please try again later.'},
        #         status=status.HTTP_429_TOO_MANY_REQUESTS
        #     )


        
        if 'file' not in request.FILES:
            return Response(
                {'error': 'No file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        file = request.FILES['file']
        
        # file val
        from ano_backend.file_validators import validate_uploaded_file
        from django.core.exceptions import ValidationError as DjangoValidationError
        
        try:
            validate_uploaded_file(file, file_type='image')
        except DjangoValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # compress and save img
        try:
            from PIL import Image
            import io
            import os
            import uuid
            import re
            
            # sanitize filename , remove path separators and dangerous chars
            safe_name = re.sub(r'[^\w\-_\.]', '_', file.name)
            safe_name = safe_name[:100]  
            if not safe_name:
                safe_name = 'image.jpg'
            
            img = Image.open(file)
            
            img.verify()
            
            # Reopen for processing (verify() closes img)
            file.seek(0)
            img = Image.open(file)
            
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
            
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
            media_path = os.path.join(settings.MEDIA_ROOT, 'chat_media')
            os.makedirs(media_path, exist_ok=True)
            
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
                if counter > 100:  
                    break
            

            temp_path = f"{file_path}.tmp"
            try:
                with open(temp_path, 'wb') as f:
                    f.write(output.getvalue())
                os.rename(temp_path, file_path)
            except Exception as e:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                raise e
            

            request_scheme = 'https' if request.is_secure() else 'http'
            request_host = request.get_host()
            media_url = f"{request_scheme}://{request_host}{settings.MEDIA_URL}chat_media/{file_name}"
            
            # Increment upload counter for rate limiting
            # cache.set(cache_key, upload_count + 1, 3600) 
            
            return Response({'media_url': media_url}, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to process image: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MessageViewSet(viewsets.ViewSet):
    """ViewSet for Message operations"""
    
    permission_classes = [IsAuthenticated]
    
    def update(self, request, pk=None):
        """Edit a message"""
        message = get_object_or_404(Message, pk=pk)
        
        # Get user's profile
        try:
            profile = request.user.profile
        except:
            return Response(
                {'error': 'Profile not found.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user is the sender
        if message.sender != profile:
            return Response(
                {'error': 'You can only edit your own messages.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if message is already deleted
        if message.is_deleted:
            return Response(
                {'error': 'Cannot edit a deleted message.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = MessageUpdateSerializer(message, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(is_edited=True)
            response_serializer = MessageSerializer(message)
            return Response(response_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, pk=None):
        """Delete a message (soft delete)"""
        message = get_object_or_404(Message, pk=pk)
        
        
        try:
            profile = request.user.profile
        except:
            return Response(
                {'error': 'Profile not found.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user is the sender
        if message.sender != profile:
            return Response(
                {'error': 'You can only delete your own messages.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Soft delete
        message.is_deleted = True
        message.content = '[Message deleted]'
        message.media_url = ''
        message.save()
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @require_privilege_drf('vote')
    @action(detail=True, methods=['post'])
    def react(self, request, pk=None):
        """Add a reaction to a message"""
        message = get_object_or_404(Message, pk=pk)
        
        
        try:
            profile = request.user.profile
        except:
            return Response(
                {'error': 'Profile not found.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = ReactionCreateSerializer(data=request.data)
        if serializer.is_valid():
            emoji = serializer.validated_data['emoji']
            
            # Create or get existing reaction
            reaction, created = MessageReaction.objects.get_or_create(
                message=message,
                profile=profile,
                emoji=emoji
            )
            
            response_serializer = MessageReactionSerializer(reaction)
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def pin(self, request, pk=None):
        """Pin or unpin a message"""
        message = get_object_or_404(Message, pk=pk)
        
        # If currently pinned, just unpin it
        if message.is_pinned:
            message.is_pinned = False
            message.pin_expires_at = None
        else:
            # Pin the message with duration
            message.is_pinned = True
            duration_hours = request.data.get('duration_hours')
            
            if duration_hours:
                from django.utils import timezone
                from datetime import timedelta
                try:
                    hours = int(duration_hours)
                    if hours > 0:
                        message.pin_expires_at = timezone.now() + timedelta(hours=hours)
                    else:
                        message.pin_expires_at = None
                except ValueError:
                    message.pin_expires_at = None
            else:
                message.pin_expires_at = None
                
        message.save()
        
        serializer = MessageSerializer(message)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def optimize_media(self, request):
        """
        Optimize media for mobile devices
        Query parameters:
        - url: media URL to optimize
        - size: target size (small, medium, large)
        """
        from django.http import HttpResponse
        import requests
        
        media_url = request.query_params.get('url', '')
        size = request.query_params.get('size', 'medium')
        
        if not media_url:
            return Response(
                {'error': 'Media URL is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Define size presets for mobile optimization
        size_presets = {
            'small': (320, 320, 70),   # width, height, quality
            'medium': (640, 640, 80),
            'large': (1024, 1024, 85),
        }
        
        max_width, max_height, quality = size_presets.get(size, size_presets['medium'])
        
        try:
            # Check if it's a local media file
            if media_url.startswith(settings.MEDIA_URL):
                # Extract file path from URL
                file_path = media_url.replace(settings.MEDIA_URL, '')
                full_path = os.path.join(settings.MEDIA_ROOT, file_path)
                
                if not os.path.exists(full_path):
                    return Response(
                        {'error': 'Media file not found'},
                        status=status.HTTP_404_NOT_FOUND
                    )
                
                # Open and optimize image
                img = Image.open(full_path)
                
                # Convert RGBA to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                
                # Resize for mobile
                img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                
                output = io.BytesIO()
                img.save(output, format='JPEG', quality=quality, optimize=True)
                output.seek(0)
                
                # Return optimized image
                response = HttpResponse(output.getvalue(), content_type='image/jpeg')
                response['Cache-Control'] = 'public, max-age=86400'  # Cache for 24 hours
                return response
            else:
                return Response(
                    {'error': 'Only local media files can be optimized'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            return Response(
                {'error': f'Failed to optimize media: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_messages(request):
    """
    Search messages across all accessible chats (chatrooms and matches)
    Query parameter: q (search query)
    """
    query = request.query_params.get('q', '').strip()
    
    if not query:
        return Response(
            {'error': 'Search query is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        profile = request.user.profile
    except:
        return Response(
            {'error': 'Profile not found.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get all matches where user is a participant
    user_matches = Match.objects.filter(
        Q(profile1=profile) | Q(profile2=profile),
        is_active=True
    ).values_list('id', flat=True)
    
    # Create search query
    search_query = SearchQuery(query)
    
    # Search in accessible messages:
    # 1. All chatroom messages (public)
    # 2. Match messages where user is a participant
    messages = Message.objects.filter(
        Q(chatroom__isnull=False) | Q(match__id__in=user_matches),
        is_deleted=False,
        search_vector=search_query
    ).select_related(
        'sender', 'chatroom', 'match'
    ).annotate(
        rank=SearchRank('search_vector', search_query)
    ).order_by('-rank', '-created_at')[:50]  # Limit to 50 results
    
    # Serialize results with highlighting
    serializer = MessageSearchResultSerializer(
        messages,
        many=True,
        context={'query': query}
    )
    
    return Response({
        'query': query,
        'count': len(messages),
        'results': serializer.data
    })


class PollViewSet(viewsets.ViewSet):
    """ViewSet for Poll operations"""
    
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """List polls in a chatroom"""
        chatroom_id = request.query_params.get('chatroom_id')
        if not chatroom_id:
            return Response(
                {'error': 'chatroom_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            chatroom = Chatroom.objects.get(id=chatroom_id, is_active=True)
        except Chatroom.DoesNotExist:
            return Response(
                {'error': 'Chatroom not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        polls = Poll.objects.filter(chatroom=chatroom, is_active=True).order_by('-created_at')
        serializer = PollSerializer(polls, many=True, context={'request': request})
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):
        """Get poll details"""
        poll = get_object_or_404(Poll, pk=pk, is_active=True)
        serializer = PollSerializer(poll, context={'request': request})
        return Response(serializer.data)
    
    @require_privilege_drf('create_polls')
    def create(self, request):
        """Create a new poll"""
        chatroom_id = request.data.get('chatroom_id')
        if not chatroom_id:
            return Response(
                {'error': 'chatroom_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            chatroom = Chatroom.objects.get(id=chatroom_id, is_active=True)
        except Chatroom.DoesNotExist:
            return Response(
                {'error': 'Chatroom not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            profile = request.user.profile
        except:
            return Response(
                {'error': 'Profile not found.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = PollCreateSerializer(data=request.data)
        if serializer.is_valid():
            poll = serializer.save(chatroom=chatroom, creator=profile)
            response_serializer = PollSerializer(poll, context={'request': request})
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @require_privilege_drf('vote')
    @action(detail=True, methods=['post'])
    def vote(self, request, pk=None):
        """Vote on a poll"""
        poll = get_object_or_404(Poll, pk=pk, is_active=True)
        
        # Check if poll is expired
        from django.utils import timezone
        if poll.expires_at and timezone.now() > poll.expires_at:
            return Response(
                {'error': 'Poll has expired'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            profile = request.user.profile
        except:
            return Response(
                {'error': 'Profile not found.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = PollVoteSerializer(data=request.data, context={'poll': poll})
        if serializer.is_valid():
            option_index = serializer.validated_data['option_index']
            
            # Create or update vote
            vote, created = PollVote.objects.update_or_create(
                poll=poll,
                voter=profile,
                defaults={'option_index': option_index}
            )
            
            # Return updated poll data
            response_serializer = PollSerializer(poll, context={'request': request})
            return Response(response_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConfessionViewSet(viewsets.ViewSet):
    """ViewSet for Confession operations"""
    
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """List approved confessions in a chatroom"""
        chatroom_id = request.query_params.get('chatroom_id')
        if not chatroom_id:
            return Response(
                {'error': 'chatroom_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            chatroom = Chatroom.objects.get(id=chatroom_id, is_active=True)
        except Chatroom.DoesNotExist:
            return Response(
                {'error': 'Chatroom not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        confessions = Confession.objects.filter(
            chatroom=chatroom,
            is_approved=True,
            is_active=True
        ).order_by('-approved_at')
        
        serializer = ConfessionSerializer(confessions, many=True)
        return Response(serializer.data)
    
    @require_privilege_drf('create_confessions')
    def create(self, request):
        """Create a new confession"""
        chatroom_id = request.data.get('chatroom_id')
        if not chatroom_id:
            return Response(
                {'error': 'chatroom_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            chatroom = Chatroom.objects.get(id=chatroom_id, is_active=True)
        except Chatroom.DoesNotExist:
            return Response(
                {'error': 'Chatroom not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            profile = request.user.profile
        except:
            return Response(
                {'error': 'Profile not found.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = ConfessionCreateSerializer(data=request.data)
        if serializer.is_valid():
            confession = serializer.save(chatroom=chatroom, creator=profile)
            response_serializer = ConfessionSerializer(confession)
            return Response({
                'message': 'Confession submitted for approval',
                'confession': response_serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)