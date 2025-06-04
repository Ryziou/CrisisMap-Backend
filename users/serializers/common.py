from rest_framework import serializers
from ..models import User
from django.contrib.auth import password_validation

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    password_confirmation = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'password', 'password_confirmation']

    def validate(self, data):
        password = data.get('password')
        password_confirmation = data.get('password_confirmation')

        if password or password_confirmation:
            if password != password_confirmation:
                raise serializers.ValidationError({ 'password': 'Passwords do not match!'})
            password_validation.validate_password(password)

        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirmation')
        return User.objects.create_user(**validated_data)
    
    def update(self, instance, validated_data):
        if 'password' in validated_data:
            password = validated_data.pop('password', None)
            validated_data.pop('password_confirmation', None)
            password_validation.validate_password(password, instance)
            instance.set_password(password)

        return super().update(instance, validated_data)