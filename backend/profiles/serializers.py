from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import Profile
from ano_backend.file_validators import validate_uploaded_file


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for Profile model - ensures no personal information is exposed"""
    
    avatar = serializers.SerializerMethodField()
    
    class Meta:
        model = Profile
        fields = [
            'id',
            'anonymous_id',
            'age',
            'interests',
            'hobbies',
            'relationship_intent',
            'personality_tags',
            'bio',
            'avatar',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'anonymous_id', 'created_at', 'updated_at']
    
    def get_avatar(self, obj):
        """Return absolute URL for avatar"""
        if obj.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            return obj.avatar.url
        return None
    
    def validate_age(self, value):
        """Validate age is between 18 and 100"""
        if value < 18 or value > 100:
            raise serializers.ValidationError("Age must be between 18 and 100")
        return value
    
    def validate_interests(self, value):
        """Validate interests is a list of strings"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Interests must be a list")
        if not all(isinstance(item, str) for item in value):
            raise serializers.ValidationError("All interests must be strings")
        return value
    
    def validate_hobbies(self, value):
        """Validate hobbies is a list of strings"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Hobbies must be a list")
        if not all(isinstance(item, str) for item in value):
            raise serializers.ValidationError("All hobbies must be strings")
        return value
    
    def validate_personality_tags(self, value):
        """Validate personality_tags is a list of strings"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Personality tags must be a list")
        if not all(isinstance(item, str) for item in value):
            raise serializers.ValidationError("All personality tags must be strings")
        return value
    
    def validate_relationship_intent(self, value):
        """Validate relationship_intent is one of the allowed choices"""
        allowed_choices = ['friendship', 'dating', 'casual']
        if value not in allowed_choices:
            raise serializers.ValidationError(
                f"Relationship intent must be one of: {', '.join(allowed_choices)}"
            )
        return value
    
    def validate_avatar(self, value):
        """Validate uploaded avatar file"""
        if value:
            try:
                validate_uploaded_file(value, file_type='image')
            except DjangoValidationError as e:
                raise serializers.ValidationError(str(e))
        return value


class ProfileCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new profile"""
    
    class Meta:
        model = Profile
        fields = [
            'age',
            'interests',
            'hobbies',
            'relationship_intent',
            'personality_tags',
            'bio',
            'avatar',
        ]
    
    def validate_age(self, value):
        """Validate age is between 18 and 100"""
        if value < 18 or value > 100:
            raise serializers.ValidationError("Age must be between 18 and 100")
        return value
    
    def validate_interests(self, value):
        """Validate interests is a list of strings"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Interests must be a list")
        if not all(isinstance(item, str) for item in value):
            raise serializers.ValidationError("All interests must be strings")
        return value
    
    def validate_hobbies(self, value):
        """Validate hobbies is a list of strings"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Hobbies must be a list")
        if not all(isinstance(item, str) for item in value):
            raise serializers.ValidationError("All hobbies must be strings")
        return value
    
    def validate_personality_tags(self, value):
        """Validate personality_tags is a list of strings"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Personality tags must be a list")
        if not all(isinstance(item, str) for item in value):
            raise serializers.ValidationError("All personality tags must be strings")
        return value
    
    def validate_relationship_intent(self, value):
        """Validate relationship_intent is one of the allowed choices"""
        allowed_choices = ['friendship', 'dating', 'casual']
        if value not in allowed_choices:
            raise serializers.ValidationError(
                f"Relationship intent must be one of: {', '.join(allowed_choices)}"
            )
        return value
    
    def validate_avatar(self, value):
        """Validate uploaded avatar file"""
        if value:
            try:
                validate_uploaded_file(value, file_type='image')
            except DjangoValidationError as e:
                raise serializers.ValidationError(str(e))
        return value
    
    def create(self, validated_data):
        """Create profile with the authenticated user"""
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)
