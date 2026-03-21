from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid


class UserProfile(models.Model):
    """
    Extended user profile for SD20 application.
    Links to Django's built-in User model and adds Patreon-specific fields.
    """
    USER_TYPE_CHOICES = [
        ('patreon', 'Patreon Member'),
        ('permanent', 'Permanent Member'),
    ]

    SUBSCRIPTION_STATUS_CHOICES = [
        ('active_patron', 'Active Patron'),
        ('declined_patron', 'Declined Patron'),
        ('former_patron', 'Former Patron'),
        ('never_patron', 'Never Patron'),
    ]

    # Link to Django User
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )

    # Unique identifier for API references
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True
    )

    # User type and permissions
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='patreon'
    )
    is_admin = models.BooleanField(default=False)

    # Patreon integration
    patreon_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        unique=True
    )
    patreon_email = models.EmailField(blank=True, null=True)
    patreon_access_token = models.TextField(blank=True, null=True)
    patreon_refresh_token = models.TextField(blank=True, null=True)

    # Subscription tracking
    subscription_status = models.CharField(
        max_length=50,
        choices=SUBSCRIPTION_STATUS_CHOICES,
        default='never_patron',
        blank=True,
        null=True
    )
    subscription_tier = models.CharField(max_length=100, blank=True, null=True)
    last_charge_date = models.DateTimeField(blank=True, null=True)
    last_charge_status = models.CharField(max_length=50, blank=True, null=True)

    # Account status
    account_locked = models.BooleanField(default=False)
    lock_date = models.DateTimeField(blank=True, null=True)
    grace_period_notified = models.BooleanField(default=False)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(blank=True, null=True)

    # Limits (can be overridden per-user)
    max_characters = models.IntegerField(default=10)
    max_campaigns_as_gm = models.IntegerField(default=5)

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f"{self.user.username} ({self.user_type})"

    def save(self, *args, **kwargs):
        # Admins must be permanent members, not patreon members
        if self.is_admin and self.user_type == 'patreon':
            self.user_type = 'permanent'
        super().save(*args, **kwargs)

    @property
    def is_active_subscriber(self):
        """Check if user has active subscription access."""
        if self.user_type == 'permanent':
            return True
        if self.is_admin:
            return True
        return self.subscription_status == 'active_patron' and not self.account_locked

    @property
    def character_count(self):
        """Get count of user's characters."""
        return self.characters.filter(is_active=True).count()

    @property
    def can_create_character(self):
        """Check if user can create another character."""
        if self.is_admin:
            return True
        return self.character_count < self.max_characters


# Signal to create UserProfile when User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
