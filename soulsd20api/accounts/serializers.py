from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile


class UserSerializer(serializers.ModelSerializer):
    """Serializer for Django's built-in User model."""

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile with nested User data."""

    user = UserSerializer(read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    character_count = serializers.IntegerField(read_only=True)
    can_create_character = serializers.BooleanField(read_only=True)
    is_active_subscriber = serializers.BooleanField(read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'uuid',
            'user',
            'username',
            'email',
            'user_type',
            'is_admin',
            'subscription_status',
            'subscription_tier',
            'account_locked',
            'max_characters',
            'max_campaigns_as_gm',
            'character_count',
            'can_create_character',
            'is_active_subscriber',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'uuid',
            'user',
            'user_type',
            'is_admin',
            'subscription_status',
            'subscription_tier',
            'account_locked',
            'created_at',
            'updated_at',
        ]


class UserProfileMinimalSerializer(serializers.ModelSerializer):
    """Minimal serializer for UserProfile (for embedding in other serializers)."""

    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = UserProfile
        fields = ['uuid', 'username']
        read_only_fields = ['uuid', 'username']


class MeSerializer(serializers.ModelSerializer):
    """
    Serializer for the /auth/me endpoint.
    Returns current user's profile with all relevant data.
    """

    id = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    character_count = serializers.IntegerField(read_only=True)
    can_create_character = serializers.BooleanField(read_only=True)
    is_active_subscriber = serializers.BooleanField(read_only=True)
    patreon_connected = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            'id',
            'uuid',
            'username',
            'user_type',
            'is_admin',
            'patreon_id',
            'patreon_email',
            'patreon_connected',
            'subscription_status',
            'subscription_tier',
            'last_charge_date',
            'account_locked',
            'grace_period_notified',
            'max_characters',
            'max_campaigns_as_gm',
            'character_count',
            'can_create_character',
            'is_active_subscriber',
            'created_at',
        ]
        read_only_fields = fields

    def get_patreon_connected(self, obj):
        """Check if Patreon tokens are present."""
        return bool(obj.patreon_access_token)
