"""
Admin configuration for normalized character models.
"""

from django.contrib import admin
from .models import (
    Character,
    CharacterStats,
    CharacterCreationStats,
    CharacterSkills,
    CharacterKnowledge,
    CharacterResources,
    CharacterResistances,
    CharacterStatuses,
    CharacterCombatSettings,
    CharacterProficiencyPoints,
    CharacterMiscData,
    CharacterEquipmentSlot,
    CharacterWeaponProficiency,
    CharacterLearnedSpell,
    CharacterAttunedSpell,
    CharacterLearnedSpirit,
    CharacterAttunedSpirit,
    CharacterLearnedWeaponSkill,
    CharacterAttunedWeaponSkill,
    CharacterObtainedFeat,
    CharacterCompanion,
    CharacterInventoryItem,
    CharacterCampaignMembership,
)


# =============================================================================
# INLINE ADMINS (One-to-One)
# =============================================================================

class CharacterStatsInline(admin.StackedInline):
    model = CharacterStats
    extra = 0
    max_num = 1


class CharacterCreationStatsInline(admin.StackedInline):
    model = CharacterCreationStats
    extra = 0
    max_num = 1


class CharacterSkillsInline(admin.StackedInline):
    model = CharacterSkills
    extra = 0
    max_num = 1


class CharacterKnowledgeInline(admin.StackedInline):
    model = CharacterKnowledge
    extra = 0
    max_num = 1


class CharacterResourcesInline(admin.StackedInline):
    model = CharacterResources
    extra = 0
    max_num = 1
    classes = ['collapse']


class CharacterResistancesInline(admin.StackedInline):
    model = CharacterResistances
    extra = 0
    max_num = 1
    classes = ['collapse']


class CharacterStatusesInline(admin.StackedInline):
    model = CharacterStatuses
    extra = 0
    max_num = 1
    classes = ['collapse']


class CharacterCombatSettingsInline(admin.StackedInline):
    model = CharacterCombatSettings
    extra = 0
    max_num = 1
    classes = ['collapse']


class CharacterProficiencyPointsInline(admin.StackedInline):
    model = CharacterProficiencyPoints
    extra = 0
    max_num = 1


class CharacterMiscDataInline(admin.StackedInline):
    model = CharacterMiscData
    extra = 0
    max_num = 1
    classes = ['collapse']


# =============================================================================
# INLINE ADMINS (One-to-Many)
# =============================================================================

class CharacterEquipmentSlotInline(admin.TabularInline):
    model = CharacterEquipmentSlot
    extra = 0


class CharacterWeaponProficiencyInline(admin.TabularInline):
    model = CharacterWeaponProficiency
    extra = 0


class CharacterLearnedSpellInline(admin.TabularInline):
    model = CharacterLearnedSpell
    extra = 0


class CharacterAttunedSpellInline(admin.TabularInline):
    model = CharacterAttunedSpell
    extra = 0


class CharacterLearnedSpiritInline(admin.TabularInline):
    model = CharacterLearnedSpirit
    extra = 0


class CharacterAttunedSpiritInline(admin.TabularInline):
    model = CharacterAttunedSpirit
    extra = 0


class CharacterLearnedWeaponSkillInline(admin.TabularInline):
    model = CharacterLearnedWeaponSkill
    extra = 0


class CharacterAttunedWeaponSkillInline(admin.TabularInline):
    model = CharacterAttunedWeaponSkill
    extra = 0


class CharacterObtainedFeatInline(admin.TabularInline):
    model = CharacterObtainedFeat
    extra = 0


class CharacterCompanionInline(admin.StackedInline):
    model = CharacterCompanion
    extra = 0
    classes = ['collapse']


class CharacterInventoryItemInline(admin.TabularInline):
    model = CharacterInventoryItem
    extra = 0


class CharacterCampaignMembershipInline(admin.TabularInline):
    model = CharacterCampaignMembership
    extra = 0
    readonly_fields = ['joined_at']


# =============================================================================
# MAIN CHARACTER ADMIN
# =============================================================================

@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    """Admin for Character model with all related inlines."""
    list_display = (
        'name',
        'level',
        'owner_username',
        'background_id',
        'lineage_id',
        'is_finalized',
        'is_active',
        'last_played',
    )
    list_filter = (
        'is_finalized',
        'is_active',
        'level',
        'gender',
        'background_id',
        'lineage_id',
    )
    search_fields = ('name', 'owner__user__username', 'id')
    readonly_fields = ('id', 'created_at', 'updated_at', 'last_played')
    ordering = ('-last_played',)

    fieldsets = (
        ('Identity', {
            'fields': ('id', 'name', 'gender', 'physical_description', 'owner')
        }),
        ('Character Creation', {
            'fields': ('background_id', 'lineage_id', 'bloodline_id', 'level', 'souls_level', 'is_finalized')
        }),
        ('Status', {
            'fields': ('is_active', 'image_url')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'last_played'),
            'classes': ('collapse',)
        }),
    )

    # Include all inlines for comprehensive character management
    inlines = [
        CharacterStatsInline,
        CharacterSkillsInline,
        CharacterKnowledgeInline,
        CharacterProficiencyPointsInline,
        CharacterResourcesInline,
        CharacterResistancesInline,
        CharacterStatusesInline,
        CharacterCombatSettingsInline,
        CharacterCreationStatsInline,
        CharacterMiscDataInline,
        CharacterEquipmentSlotInline,
        CharacterWeaponProficiencyInline,
        CharacterLearnedSpellInline,
        CharacterAttunedSpellInline,
        CharacterLearnedSpiritInline,
        CharacterAttunedSpiritInline,
        CharacterLearnedWeaponSkillInline,
        CharacterAttunedWeaponSkillInline,
        CharacterObtainedFeatInline,
        CharacterCompanionInline,
        CharacterInventoryItemInline,
        CharacterCampaignMembershipInline,
    ]

    def owner_username(self, obj):
        """Display owner's username."""
        if obj.owner and obj.owner.user:
            return obj.owner.user.username
        return '-'
    owner_username.short_description = 'Owner'
    owner_username.admin_order_field = 'owner__user__username'

    def get_queryset(self, request):
        """Optimize query with select_related."""
        return super().get_queryset(request).select_related('owner__user')


# =============================================================================
# STANDALONE ADMINS (for browsing related data independently)
# =============================================================================

@admin.register(CharacterEquipmentSlot)
class CharacterEquipmentSlotAdmin(admin.ModelAdmin):
    """Admin for browsing all equipment slots."""
    list_display = ('character', 'slot_type', 'item_name', 'item_category', 'item_id')
    list_filter = ('slot_type', 'item_category')
    search_fields = ('character__name', 'item_name')
    raw_id_fields = ('character',)


@admin.register(CharacterWeaponProficiency)
class CharacterWeaponProficiencyAdmin(admin.ModelAdmin):
    """Admin for browsing all weapon proficiencies."""
    list_display = ('character', 'weapon_tree', 'level')
    list_filter = ('weapon_tree', 'level')
    search_fields = ('character__name',)
    raw_id_fields = ('character',)


@admin.register(CharacterObtainedFeat)
class CharacterObtainedFeatAdmin(admin.ModelAdmin):
    """Admin for browsing all obtained feats."""
    list_display = ('character', 'feat_id', 'feat_type', 'weapon_tree', 'source')
    list_filter = ('feat_type', 'weapon_tree')
    search_fields = ('character__name',)
    raw_id_fields = ('character',)


@admin.register(CharacterCompanion)
class CharacterCompanionAdmin(admin.ModelAdmin):
    """Admin for browsing all companions."""
    list_display = ('name', 'character', 'companion_type', 'hp', 'fp', 'ap')
    list_filter = ('companion_type',)
    search_fields = ('name', 'character__name')
    raw_id_fields = ('character',)
