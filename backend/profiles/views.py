from rest_framework import status, generics, parsers
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Profile
from .serializers import ProfileSerializer


class ProfileMeView(generics.RetrieveUpdateAPIView):
    """Get or update the authenticated user's profile"""
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        """Get or create the profile for the authenticated user"""
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile


class ProfileDetailView(generics.RetrieveAPIView):
    """Get a profile by anonymous_id (public endpoint)"""
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'anonymous_id'
    queryset = Profile.objects.all()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([parsers.MultiPartParser, parsers.FormParser])
def upload_avatar(request):
    """Upload avatar for the authenticated user's profile"""
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        return Response(
            {'error': 'Profile does not exist'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if 'avatar' not in request.FILES:
        return Response(
            {'error': 'No avatar file provided'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    avatar_file = request.FILES['avatar']
    
    # Validate file type
    allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
    if avatar_file.content_type not in allowed_types:
        return Response(
            {'error': 'Invalid file type. Only JPEG, PNG, and GIF are allowed'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate file size (max 5MB)
    max_size = 5 * 1024 * 1024  # 5MB in bytes
    if avatar_file.size > max_size:
        return Response(
            {'error': 'File size too large. Maximum size is 5MB'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Save the avatar
    profile.avatar = avatar_file
    profile.save()
    
    serializer = ProfileSerializer(profile)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def optimize_avatar(request):
    """
    Optimize avatar images for mobile devices
    Query parameters:
    - anonymous_id: profile anonymous ID
    - size: target size (small, medium, large)
    """
    from django.http import HttpResponse
    from PIL import Image
    import io
    import os
    
    anonymous_id = request.query_params.get('anonymous_id', '')
    size = request.query_params.get('size', 'medium')
    
    if not anonymous_id:
        return Response(
            {'error': 'Anonymous ID is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Define size presets for mobile optimization
    size_presets = {
        'small': (150, 150, 70),   # width, height, quality
        'medium': (300, 300, 80),
        'large': (600, 600, 85),
    }
    
    max_width, max_height, quality = size_presets.get(size, size_presets['medium'])
    
    try:
        profile = Profile.objects.get(anonymous_id=anonymous_id)
        
        if not profile.avatar:
            return Response(
                {'error': 'Profile has no avatar'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Open and optimize image
        img = Image.open(profile.avatar.path)
        
        # Convert RGBA to RGB if necessary
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        
        # Resize for mobile
        img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        
        # Save to bytes
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=quality, optimize=True)
        output.seek(0)
        
        # Return optimized image
        response = HttpResponse(output.getvalue(), content_type='image/jpeg')
        response['Cache-Control'] = 'public, max-age=86400'  # Cache for 24 hours
        return response
        
    except Profile.DoesNotExist:
        return Response(
            {'error': 'Profile not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Failed to optimize avatar: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
