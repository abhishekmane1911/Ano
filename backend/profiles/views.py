from rest_framework import status, generics, parsers
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Profile
from .serializers import ProfileSerializer
from django.conf import settings


class ProfileMeView(generics.RetrieveUpdateAPIView):
    """Get or update the authenticated user's profile"""
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
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
    from ano_backend.file_validators import validate_uploaded_file
    from django.core.exceptions import ValidationError

    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        return Response({'error': 'Profile does not exist'}, status=status.HTTP_404_NOT_FOUND)

    avatar_file = request.FILES.get('avatar')
    if not avatar_file:
        return Response({'error': 'No avatar file provided'}, status=status.HTTP_400_BAD_REQUEST)

    if avatar_file.size > settings.MAX_AVATAR_SIZE:
        return Response({'error': 'File size too large. Maximum size is 5MB'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Validates: magic-byte MIME type, extension, Pillow integrity, dimensions
        validate_uploaded_file(avatar_file, file_type='image')
    except ValidationError as e:
        return Response({'error': e.message}, status=status.HTTP_400_BAD_REQUEST)

    profile.avatar = avatar_file
    profile.save()

    return Response(ProfileSerializer(profile).data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def optimize_avatar(request):
    from django.http import HttpResponse
    from PIL import Image
    import io
    
    anonymous_id = request.query_params.get('anonymous_id', '')
    size = request.query_params.get('size', 'medium')
    
    if not anonymous_id:
        return Response({'error': 'Anonymous ID is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    size_presets = {
        'small': (150, 150, 70),
        'medium': (300, 300, 80),
        'large': (600, 600, 85),
    }
    
    max_width, max_height, quality = size_presets.get(size, size_presets['medium'])
    
    try:
        profile = Profile.objects.get(anonymous_id=anonymous_id)
        if not profile.avatar:
            return Response({'error': 'Profile has no avatar'}, status=status.HTTP_404_NOT_FOUND)
        
        Image.MAX_IMAGE_PIXELS = 10000000  # 10MP decompression bomb protection
        img = Image.open(profile.avatar.path)
        
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        
        img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=quality, optimize=True)
        output.seek(0)
        
        response = HttpResponse(output.getvalue(), content_type='image/jpeg')
        response['Cache-Control'] = 'public, max-age=86400'
        return response
        
    except Profile.DoesNotExist:
        return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': f'Failed to optimize avatar: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
