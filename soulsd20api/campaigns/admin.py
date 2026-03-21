from django.contrib import admin
from .models import Campaign, CampaignMembership, CampaignInvite


class CampaignMembershipInline(admin.TabularInline):
    model = CampaignMembership
    extra = 0
    readonly_fields = ['joined_at', 'updated_at']


class CampaignInviteInline(admin.TabularInline):
    model = CampaignInvite
    extra = 0
    fk_name = 'campaign'
    readonly_fields = ['created_at', 'responded_at']


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ['name', 'gm', 'player_count', 'max_players', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'gm__user__username']
    readonly_fields = ['id', 'invite_code', 'created_at', 'updated_at']
    inlines = [CampaignMembershipInline, CampaignInviteInline]

    fieldsets = (
        ('Identity', {
            'fields': ('id', 'name', 'description', 'image_url')
        }),
        ('Game Master', {
            'fields': ('gm',)
        }),
        ('Settings', {
            'fields': ('max_players',)
        }),
        ('Invite System', {
            'fields': ('invite_code', 'invite_enabled')
        }),
        ('Campaign Settings (JSON)', {
            'fields': ('settings',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'last_session')
        }),
    )


@admin.register(CampaignMembership)
class CampaignMembershipAdmin(admin.ModelAdmin):
    list_display = ['user', 'campaign', 'role', 'status', 'joined_at']
    list_filter = ['role', 'status', 'joined_at']
    search_fields = ['user__user__username', 'campaign__name']
    readonly_fields = ['id', 'joined_at', 'updated_at']


@admin.register(CampaignInvite)
class CampaignInviteAdmin(admin.ModelAdmin):
    list_display = ['invited_user', 'campaign', 'invited_by', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['invited_user__user__username', 'campaign__name']
    readonly_fields = ['id', 'created_at', 'responded_at']
