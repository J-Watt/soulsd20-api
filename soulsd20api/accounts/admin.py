from datetime import timedelta

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django import forms
from django.utils import timezone
from .models import UserProfile, AccountAuditLog, AuthToken


class UserProfileInlineForm(forms.ModelForm):
    """Custom form for UserProfile inline with validation."""
    class Meta:
        model = UserProfile
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        is_admin = cleaned_data.get('is_admin')
        user_type = cleaned_data.get('user_type')

        if is_admin and user_type == 'patreon':
            raise forms.ValidationError(
                "Admins cannot be Patreon Members. Please set user type to 'Permanent Member'."
            )
        return cleaned_data


class UserProfileInline(admin.StackedInline):
    """Inline admin for UserProfile on the User admin page."""
    model = UserProfile
    form = UserProfileInlineForm
    can_delete = False
    verbose_name_plural = 'Profile'
    readonly_fields = ['uuid', 'created_at', 'updated_at', 'character_count']

    fieldsets = (
        ('Account Type', {
            'fields': ('user_type', 'is_admin')
        }),
        ('Patreon Integration', {
            'fields': ('patreon_id', 'patreon_email'),
            'classes': ('collapse',)
        }),
        ('Subscription Status', {
            'fields': (
                'subscription_status',
                'subscription_tier',
                'last_charge_date',
                'last_charge_status',
            )
        }),
        ('Account Status', {
            'fields': ('account_locked', 'lock_reason', 'lock_date', 'grace_period_notified')
        }),
        ('Limits', {
            'fields': ('max_characters', 'max_campaigns_as_gm', 'character_count')
        }),
        ('Metadata', {
            'fields': ('uuid', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class AccountAuditLogInline(admin.TabularInline):
    model = AccountAuditLog
    extra = 0
    can_delete = False
    readonly_fields = ('timestamp', 'event', 'old_status', 'new_status', 'old_lock_date', 'new_lock_date', 'actor', 'note')
    fields = readonly_fields
    ordering = ('-timestamp',)

    def has_add_permission(self, request, obj=None):
        return False


# Replace default User admin with custom version including UserProfile inline
class UserAdmin(BaseUserAdmin):
    """Custom User admin with UserProfile inline."""
    inlines = (UserProfileInline,)
    list_display = (
        'username',
        'get_user_type',
        'get_subscription_status',
        'get_admin_panel_access',
    )
    # Override list_filter to remove 'is_staff' reference
    list_filter = (
        'is_active',
        'is_superuser',
        'profile__user_type',
        'profile__subscription_status',
        'profile__account_locked',
    )

    # Customize fieldsets - rename is_staff to "Admin Panel Access"
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )

    def get_admin_panel_access(self, obj):
        """Display admin panel access status."""
        return obj.is_staff
    get_admin_panel_access.short_description = 'Admin Panel Access'
    get_admin_panel_access.boolean = True
    get_admin_panel_access.admin_order_field = 'is_staff'

    def get_form(self, request, obj=None, **kwargs):
        """Override form to rename 'is_staff' label."""
        form = super().get_form(request, obj, **kwargs)
        if 'is_staff' in form.base_fields:
            form.base_fields['is_staff'].label = 'Admin Panel Access'
            form.base_fields['is_staff'].help_text = 'Can this user access the admin panel?'
        return form

    def get_inlines(self, request, obj=None):
        """Only show UserProfile inline when editing existing users, not when adding."""
        if obj:  # Editing existing user
            return self.inlines
        return []  # Adding new user - signal will create the profile

    def get_user_type(self, obj):
        if hasattr(obj, 'profile'):
            return obj.profile.user_type
        return '-'
    get_user_type.short_description = 'User Type'
    get_user_type.admin_order_field = 'profile__user_type'

    def get_subscription_status(self, obj):
        if hasattr(obj, 'profile'):
            return obj.profile.subscription_status
        return '-'
    get_subscription_status.short_description = 'Subscription'
    get_subscription_status.admin_order_field = 'profile__subscription_status'


# Re-register User with the custom admin class
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin for UserProfile model (standalone view)."""
    list_display = (
        'user',
        'user_type',
        'subscription_status',
        'account_locked',
        'lock_reason',
        'lock_date',
        'character_count',
        'created_at',
    )
    list_filter = (
        'user_type',
        'subscription_status',
        'account_locked',
        'lock_reason',
        'is_admin',
    )
    search_fields = ('user__username', 'user__email', 'patreon_id', 'patreon_email')
    readonly_fields = ('uuid', 'created_at', 'updated_at', 'character_count')
    inlines = [AccountAuditLogInline]
    actions = ['grant_thirty_days_grace']

    fieldsets = (
        ('User', {
            'fields': ('user', 'uuid')
        }),
        ('Account Type', {
            'fields': ('user_type', 'is_admin')
        }),
        ('Patreon Integration', {
            'fields': ('patreon_id', 'patreon_email', 'patreon_access_token', 'patreon_refresh_token'),
            'classes': ('collapse',)
        }),
        ('Subscription Status', {
            'fields': (
                'subscription_status',
                'subscription_tier',
                'last_charge_date',
                'last_charge_status',
            )
        }),
        ('Account Status', {
            'fields': ('account_locked', 'lock_reason', 'lock_date', 'grace_period_notified')
        }),
        ('Limits', {
            'fields': ('max_characters', 'max_campaigns_as_gm')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        """When an admin toggles account_locked or lock_date via the form,
        write an audit trail row and tag the lock reason as admin_action."""
        admin_actor = request.user.username or 'admin'
        prior = None
        if change and obj.pk:
            try:
                prior = UserProfile.objects.get(pk=obj.pk)
            except UserProfile.DoesNotExist:
                prior = None

        if prior is not None:
            if not prior.account_locked and obj.account_locked:
                if not obj.lock_reason:
                    obj.lock_reason = 'admin_action'
                super().save_model(request, obj, form, change)
                AuthToken.objects.filter(user=obj.user).delete()
                AccountAuditLog.objects.create(
                    profile=obj,
                    event='manually_locked',
                    old_status=prior.subscription_status or '',
                    new_status=obj.subscription_status or '',
                    old_lock_date=prior.lock_date,
                    new_lock_date=obj.lock_date,
                    actor=admin_actor,
                    note='admin panel',
                )
                return
            if prior.account_locked and not obj.account_locked:
                obj.lock_reason = ''
                obj.grace_period_notified = False
                super().save_model(request, obj, form, change)
                AccountAuditLog.objects.create(
                    profile=obj,
                    event='unlocked',
                    old_status=prior.subscription_status or '',
                    new_status=obj.subscription_status or '',
                    old_lock_date=prior.lock_date,
                    new_lock_date=obj.lock_date,
                    actor=admin_actor,
                    note='admin panel',
                )
                return

        super().save_model(request, obj, form, change)

    def grant_thirty_days_grace(self, request, queryset):
        actor = request.user.username or 'admin'
        new_date = timezone.now() + timedelta(days=30)
        count = 0
        for profile in queryset:
            profile.apply_unlock(actor=actor, note='grant 30 days grace', new_lock_date=new_date)
            count += 1
        self.message_user(request, f'Granted 30 days grace to {count} profile(s).')
    grant_thirty_days_grace.short_description = 'Grant 30 days grace (unlock + set lock_date to +30d)'


@admin.register(AccountAuditLog)
class AccountAuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'profile', 'event', 'old_status', 'new_status', 'actor')
    list_filter = ('event', 'actor')
    search_fields = ('profile__user__username', 'note')
    readonly_fields = ('profile', 'timestamp', 'event', 'old_status', 'new_status', 'old_lock_date', 'new_lock_date', 'actor', 'note')
    ordering = ('-timestamp',)

    def has_add_permission(self, request):
        return False
