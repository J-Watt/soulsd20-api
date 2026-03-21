from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django import forms
from .models import UserProfile


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
            'fields': ('account_locked', 'lock_date', 'grace_period_notified')
        }),
        ('Limits', {
            'fields': ('max_characters', 'max_campaigns_as_gm', 'character_count')
        }),
        ('Metadata', {
            'fields': ('uuid', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


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
        'character_count',
        'created_at',
    )
    list_filter = (
        'user_type',
        'subscription_status',
        'account_locked',
        'is_admin',
    )
    search_fields = ('user__username', 'user__email', 'patreon_id', 'patreon_email')
    readonly_fields = ('uuid', 'created_at', 'updated_at', 'character_count')

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
            'fields': ('account_locked', 'lock_date', 'grace_period_notified')
        }),
        ('Limits', {
            'fields': ('max_characters', 'max_campaigns_as_gm')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
