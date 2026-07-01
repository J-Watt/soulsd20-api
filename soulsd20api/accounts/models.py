import binascii
import os
import uuid
from datetime import timedelta

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


LOCK_GRACE_DAYS = 32
GRACE_WARNING_DAYS = 7


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
    LOCK_REASON_CHOICES = [
        ('', 'None'),
        ('patreon_lapsed', 'Patreon lapsed'),
        ('admin_action', 'Admin action'),
    ]
    account_locked = models.BooleanField(default=False)
    lock_date = models.DateTimeField(blank=True, null=True)
    lock_reason = models.CharField(
        max_length=32,
        choices=LOCK_REASON_CHOICES,
        blank=True,
        default=''
    )
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
    def is_exempt_from_lockout(self):
        return self.is_admin or self.user_type == 'permanent'

    @property
    def days_until_lockout(self):
        if self.is_exempt_from_lockout or not self.lock_date:
            return None
        delta = self.lock_date - timezone.now()
        return delta.days

    @property
    def should_show_grace_toast(self):
        if self.is_exempt_from_lockout:
            return False
        if self.subscription_status == 'active_patron':
            return False
        if self.grace_period_notified:
            return False
        days = self.days_until_lockout
        if days is None:
            return False
        return 0 < days <= GRACE_WARNING_DAYS

    def apply_patreon_status(self, new_status, last_charge_date, actor='system', note=''):
        """Update subscription state after a Patreon check. Writes an audit row.
        Rolls lock_date to last_charge_date + LOCK_GRACE_DAYS when active."""
        old_status = self.subscription_status
        old_lock_date = self.lock_date

        self.subscription_status = new_status
        if last_charge_date and self.last_charge_date != last_charge_date:
            self.last_charge_date = last_charge_date
            self.grace_period_notified = False

        if new_status == 'active_patron':
            base = self.last_charge_date or self.created_at or timezone.now()
            self.lock_date = base + timedelta(days=LOCK_GRACE_DAYS)
            if self.account_locked and self.lock_reason == 'patreon_lapsed':
                self.account_locked = False
                self.lock_reason = ''
        else:
            # Grandfathered account: no lock_date was ever set. Give them a
            # 30-day grace window from now so they have time to react to the
            # new enforcement. Existing non-null lock_date is untouched so
            # someone who unsubscribed mid-cycle does not get a free renewal.
            if self.lock_date is None:
                self.lock_date = timezone.now() + timedelta(days=30)

        self.save()

        event = 'patreon_confirmed' if new_status == 'active_patron' else 'patreon_dropped'
        AccountAuditLog.objects.create(
            profile=self,
            event=event,
            old_status=old_status or '',
            new_status=new_status or '',
            old_lock_date=old_lock_date,
            new_lock_date=self.lock_date,
            actor=actor,
            note=note,
        )

    def apply_lockout(self, reason, actor='system', note=''):
        """Force account_locked True with a specific reason, delete tokens,
        and write an audit row."""
        old_status = self.subscription_status
        old_lock_date = self.lock_date

        self.account_locked = True
        self.lock_reason = reason
        self.save()

        AuthToken.objects.filter(user=self.user).delete()

        event = 'auto_locked' if reason == 'patreon_lapsed' else 'manually_locked'
        AccountAuditLog.objects.create(
            profile=self,
            event=event,
            old_status=old_status or '',
            new_status=old_status or '',
            old_lock_date=old_lock_date,
            new_lock_date=self.lock_date,
            actor=actor,
            note=note,
        )

    def apply_unlock(self, actor='admin', note='', new_lock_date=None):
        """Clear account_locked, optionally set a new lock_date, write audit row."""
        old_lock_date = self.lock_date
        self.account_locked = False
        self.lock_reason = ''
        if new_lock_date is not None:
            self.lock_date = new_lock_date
        self.grace_period_notified = False
        self.save()

        AccountAuditLog.objects.create(
            profile=self,
            event='unlocked',
            old_status=self.subscription_status or '',
            new_status=self.subscription_status or '',
            old_lock_date=old_lock_date,
            new_lock_date=self.lock_date,
            actor=actor,
            note=note,
        )

    def mark_grace_notified(self, actor='system'):
        if self.grace_period_notified:
            return
        self.grace_period_notified = True
        self.save(update_fields=['grace_period_notified'])
        AccountAuditLog.objects.create(
            profile=self,
            event='grace_notified',
            old_status=self.subscription_status or '',
            new_status=self.subscription_status or '',
            old_lock_date=self.lock_date,
            new_lock_date=self.lock_date,
            actor=actor,
            note='',
        )

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


class AuthToken(models.Model):
    SOURCE_APP = 'app'
    SOURCE_FOUNDRY = 'foundry'
    SOURCE_CHOICES = [
        (SOURCE_APP, 'App'),
        (SOURCE_FOUNDRY, 'Foundry'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='auth_tokens'
    )
    key = models.CharField(max_length=40, unique=True, db_index=True)
    source = models.CharField(
        max_length=10,
        choices=SOURCE_CHOICES,
        default=SOURCE_APP,
        db_index=True
    )
    created = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(blank=True, null=True)
    label = models.CharField(max_length=80, blank=True, default='')

    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['user', 'source']),
        ]

    def __str__(self):
        return f"{self.source} token for {self.user.username}"

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_key():
        return binascii.hexlify(os.urandom(20)).decode()


class PairingCode(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='pairing_codes'
    )
    code = models.CharField(max_length=12, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    redeemed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.code} ({self.user.username})"

    @property
    def is_redeemed(self):
        return self.redeemed_at is not None

    @property
    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.expires_at

    @property
    def is_valid(self):
        return not self.is_redeemed and not self.is_expired


class AccountAuditLog(models.Model):
    EVENT_CHOICES = [
        ('auto_locked', 'Auto locked (Patreon lapsed)'),
        ('manually_locked', 'Manually locked (admin)'),
        ('unlocked', 'Unlocked'),
        ('grace_started', 'Grace period started'),
        ('grace_notified', 'User acknowledged grace notification'),
        ('patreon_confirmed', 'Patreon status refreshed to active'),
        ('patreon_dropped', 'Patreon status dropped from active'),
        ('signup_rejected', 'Signup rejected (not a patron)'),
    ]

    profile = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='audit_logs'
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    event = models.CharField(max_length=32, choices=EVENT_CHOICES)
    old_status = models.CharField(max_length=32, blank=True, default='')
    new_status = models.CharField(max_length=32, blank=True, default='')
    old_lock_date = models.DateTimeField(null=True, blank=True)
    new_lock_date = models.DateTimeField(null=True, blank=True)
    actor = models.CharField(max_length=100, blank=True, default='')
    note = models.CharField(max_length=200, blank=True, default='')

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['profile', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.timestamp:%Y-%m-%d %H:%M} {self.event} ({self.profile.user.username})"
