from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import Profile
from ano_backend.file_validators import validate_uploaded_file


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for Profile model to ensures no personal information is exposed"""
    
    avatar = serializers.SerializerMethodField()
    
    class Meta:
        model = Profile
        fields = [
            'id',
            'anonymous_id',
            'bio',
            'avatar',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'anonymous_id', 'created_at', 'updated_at']
    
    def get_avatar(self, obj):
        """Return absolute URL for avtr"""
        if obj.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            return obj.avatar.url
        return None
    
    
    def validate_avatar(self, value):
        """val uploaded avtr file"""
        if value:
            try:
                validate_uploaded_file(value, file_type='image')
            except DjangoValidationError as e:
                raise serializers.ValidationError(str(e))
        return value

