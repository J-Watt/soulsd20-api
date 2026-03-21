"""
Campaign Serializers for SD20 API.

Provides serializers for Campaign, CampaignMembership, and CampaignInvite models.
"""

from rest_framework import serializers
from .models import Campaign, CampaignMembership, CampaignInvite


class CampaignMembershipSerializer(serializers.ModelSerializer):
    """Serializer for campaign memberships."""
    username = serializers.CharField(source='user.user.username', read_only=True)
    user_uuid = serializers.UUIDField(source='user.uuid', read_only=True)

    class Meta:
        model = CampaignMembership
        fields = [
            'id',
            'user_uuid',
            'username',
            'role',
            'status',
            'display_name',
            'joined_at',
        ]
        read_only_fields = ['id', 'joined_at']


class CampaignListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for campaign lists."""
    gm_username = serializers.CharField(source='gm.user.username', read_only=True)
    gm_uuid = serializers.UUIDField(source='gm.uuid', read_only=True)
    player_count = serializers.IntegerField(read_only=True)
    is_full = serializers.BooleanField(read_only=True)

    class Meta:
        model = Campaign
        fields = [
            'id',
            'name',
            'description',
            'image_url',
            'gm_uuid',
            'gm_username',
            'player_count',
            'max_players',
            'is_full',
            'created_at',
            'updated_at',
            'last_session',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CampaignDetailSerializer(serializers.ModelSerializer):
    """Full serializer for campaign details (GM view)."""
    gm_username = serializers.CharField(source='gm.user.username', read_only=True)
    gm_uuid = serializers.UUIDField(source='gm.uuid', read_only=True)
    player_count = serializers.IntegerField(read_only=True)
    is_full = serializers.BooleanField(read_only=True)
    memberships = CampaignMembershipSerializer(many=True, read_only=True)

    class Meta:
        model = Campaign
        fields = [
            'id',
            'name',
            'description',
            'image_url',
            'gm_uuid',
            'gm_username',
            'max_players',
            'player_count',
            'is_full',
            'invite_code',
            'invite_enabled',
            'settings',
            'memberships',
            'created_at',
            'updated_at',
            'last_session',
        ]
        read_only_fields = ['id', 'invite_code', 'created_at', 'updated_at']


class CampaignCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating campaigns."""

    class Meta:
        model = Campaign
        fields = [
            'name',
            'description',
            'image_url',
            'max_players',
            'settings',
        ]

    def create(self, validated_data):
        # GM is set from the request user
        validated_data['gm'] = self.context['request'].user.profile
        return super().create(validated_data)


class CampaignUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating campaigns."""

    class Meta:
        model = Campaign
        fields = [
            'name',
            'description',
            'image_url',
            'max_players',
            'invite_enabled',
            'settings',
            'last_session',
        ]


class CampaignInviteSerializer(serializers.ModelSerializer):
    """Serializer for campaign invites."""
    campaign_name = serializers.CharField(source='campaign.name', read_only=True)
    invited_by_username = serializers.CharField(source='invited_by.user.username', read_only=True)
    invited_user_username = serializers.CharField(source='invited_user.user.username', read_only=True)

    class Meta:
        model = CampaignInvite
        fields = [
            'id',
            'campaign',
            'campaign_name',
            'invited_by_username',
            'invited_user_username',
            'role',
            'status',
            'message',
            'created_at',
            'expires_at',
            'responded_at',
        ]
        read_only_fields = ['id', 'campaign', 'invited_by_username', 'created_at', 'responded_at']


class CampaignInviteCreateSerializer(serializers.Serializer):
    """Serializer for creating campaign invites."""
    invited_user_uuid = serializers.UUIDField()
    role = serializers.ChoiceField(choices=CampaignMembership.ROLE_CHOICES, default='player')
    message = serializers.CharField(required=False, allow_blank=True, default='')

    def validate_invited_user_uuid(self, value):
        from accounts.models import UserProfile
        try:
            user = UserProfile.objects.get(uuid=value)
            return user
        except UserProfile.DoesNotExist:
            raise serializers.ValidationError("User not found")


class JoinCampaignSerializer(serializers.Serializer):
    """Serializer for joining a campaign via invite code."""
    invite_code = serializers.CharField(max_length=20)

    def validate_invite_code(self, value):
        try:
            campaign = Campaign.objects.get(invite_code=value.upper(), invite_enabled=True)
            if campaign.is_full:
                raise serializers.ValidationError("Campaign is full")
            return campaign
        except Campaign.DoesNotExist:
            raise serializers.ValidationError("Invalid invite code")


class AssignCharacterSerializer(serializers.Serializer):
    """Serializer for assigning a character to a campaign."""
    character_uuid = serializers.UUIDField()

    def validate_character_uuid(self, value):
        from characters.models import Character
        request = self.context.get('request')
        try:
            character = Character.objects.get(id=value, owner=request.user.profile, is_active=True)
            return character
        except Character.DoesNotExist:
            raise serializers.ValidationError("Character not found or not owned by you")
