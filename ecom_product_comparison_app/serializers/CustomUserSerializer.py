from rest_framework import serializers
from ..models import CustomUser
from datetime import datetime

class CustomUserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    full_name = serializers.CharField(required=False, allow_blank=True)
    is_active = serializers.BooleanField(default=True)
    created_at = serializers.DateTimeField(required=False)

    def create(self, validated_data):
        # Create a new user instance
        user = CustomUser(
            email=validated_data['email'],
            full_name=validated_data.get('full_name', ''),
            is_active=validated_data.get('is_active', True),
            created_at=validated_data.get('created_at', datetime.utcnow())
        )
        
        # Hash the password before saving
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        # Update existing user instance
        instance.email = validated_data.get('email', instance.email)
        instance.full_name = validated_data.get('full_name', instance.full_name)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.created_at = validated_data.get('created_at', instance.created_at)
        
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
        
        instance.save()
        return instance
