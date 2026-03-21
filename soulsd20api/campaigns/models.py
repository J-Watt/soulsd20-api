"""
Campaign Models for SD20 Application.

Campaigns are game sessions/stories managed by a GM with multiple player members.
Characters can be assigned to campaigns, and campaign data is synced via localStorage
for Foundry VTT integration.
"""

from django.db import models
import uuid


class Campaign(models.Model):
    """
    A campaign/game session managed by a GM.

    Players join campaigns via invite code or direct invitation.
    Characters are assigned to campaigns by their owners.
    """

    # Primary key - UUID for API references
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    # Campaign identity
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    image_url = models.URLField(max_length=500, blank=True, null=True)

    # Game Master (owner)
    gm = models.ForeignKey(
        'accounts.UserProfile',
        on_delete=models.CASCADE,
        related_name='gm_campaigns'
    )

    # Campaign settings
    max_players = models.IntegerField(default=6)

    # Invite system
    invite_code = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True
    )
    invite_enabled = models.BooleanField(default=True)

    # Campaign-specific settings (JSON for flexibility)
    settings = models.JSONField(default=dict, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_session = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Campaign'
        verbose_name_plural = 'Campaigns'
        indexes = [
            models.Index(fields=['gm']),
            models.Index(fields=['invite_code']),
        ]

    def __str__(self):
        return f"{self.name} (GM: {self.gm.user.username})"

    def save(self, *args, **kwargs):
        # Generate invite code if not set
        if not self.invite_code and self.invite_enabled:
            self.invite_code = self._generate_invite_code()
        super().save(*args, **kwargs)

    def _generate_invite_code(self):
        """Generate a unique 8-character invite code."""
        import random
        import string
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            if not Campaign.objects.filter(invite_code=code).exists():
                return code

    def regenerate_invite_code(self):
        """Regenerate the invite code."""
        self.invite_code = self._generate_invite_code()
        self.save(update_fields=['invite_code'])
        return self.invite_code

    @property
    def player_count(self):
        """Count of active members including GM."""
        return self.memberships.filter(
            status='active'
        ).count() + 1  # +1 for the GM who is always a member

    @property
    def is_full(self):
        """Check if campaign has reached max players."""
        return self.player_count >= self.max_players

    @property
    def active_characters(self):
        """Get all active characters in this campaign."""
        from characters.models import Character
        return Character.objects.filter(
            campaign=self,
            is_active=True
        )


class CampaignMembership(models.Model):
    """
    Membership linking users to campaigns.

    Multiple characters from the same user can be in the same campaign.
    """

    ROLE_CHOICES = [
        ('player', 'Player'),
    ]

    STATUS_CHOICES = [
        ('invited', 'Invited'),
        ('active', 'Active'),
        ('left', 'Left'),
        ('kicked', 'Kicked'),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    # Relationships
    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name='memberships'
    )
    user = models.ForeignKey(
        'accounts.UserProfile',
        on_delete=models.CASCADE,
        related_name='campaign_memberships'
    )

    # Membership details
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='player'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='invited'
    )

    # Timestamps
    joined_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Nickname for this campaign (optional)
    display_name = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['joined_at']
        verbose_name = 'Campaign Membership'
        verbose_name_plural = 'Campaign Memberships'
        unique_together = ['campaign', 'user']
        indexes = [
            models.Index(fields=['campaign', 'status']),
            models.Index(fields=['user', 'status']),
        ]

    def __str__(self):
        return f"{self.user.user.username} in {self.campaign.name} ({self.role})"

    @property
    def characters(self):
        """Get user's characters assigned to this campaign."""
        from characters.models import Character
        return Character.objects.filter(
            owner=self.user,
            campaign=self.campaign,
            is_active=True
        )


class CampaignInvite(models.Model):
    """
    Direct invitations to specific users.

    Separate from invite codes - these are direct invites sent to users.
    """

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('expired', 'Expired'),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name='invites'
    )
    invited_by = models.ForeignKey(
        'accounts.UserProfile',
        on_delete=models.CASCADE,
        related_name='sent_invites'
    )
    invited_user = models.ForeignKey(
        'accounts.UserProfile',
        on_delete=models.CASCADE,
        related_name='received_invites'
    )

    role = models.CharField(
        max_length=20,
        choices=CampaignMembership.ROLE_CHOICES,
        default='player'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    message = models.TextField(blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    responded_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Campaign Invite'
        verbose_name_plural = 'Campaign Invites'
        indexes = [
            models.Index(fields=['invited_user', 'status']),
            models.Index(fields=['campaign', 'status']),
        ]

    def __str__(self):
        return f"Invite to {self.invited_user.user.username} for {self.campaign.name}"

    def accept(self):
        """Accept the invite and create membership."""
        from django.utils import timezone

        if self.status != 'pending':
            return None

        # Create membership
        membership, created = CampaignMembership.objects.get_or_create(
            campaign=self.campaign,
            user=self.invited_user,
            defaults={
                'role': self.role,
                'status': 'active'
            }
        )

        if not created:
            # User was already a member (maybe left before)
            membership.role = self.role
            membership.status = 'active'
            membership.save()

        self.status = 'accepted'
        self.responded_at = timezone.now()
        self.save()

        return membership

    def decline(self):
        """Decline the invite."""
        from django.utils import timezone

        if self.status != 'pending':
            return False

        self.status = 'declined'
        self.responded_at = timezone.now()
        self.save()
        return True
