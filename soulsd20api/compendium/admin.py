from django.contrib import admin

from . import models

"""
Weapon Proficiency Feats (And Sub Feats)
"""


class WeaponProfSubParentInline(admin.StackedInline):
    model = models.WeaponProfSubFeat
    fk_name = "parent"
    extra = 0
    verbose_name = "Sub Feat"


class WeaponProfSubExtendsInline(admin.StackedInline):
    model = models.WeaponProfSubFeat
    fk_name = "extends"
    extra = 0
    verbose_name = "Extension"


class WeaponProfDiceInline(admin.TabularInline):
    model = models.WeaponProfDice
    extra = 0


class WeaponProfScalingInline(admin.TabularInline):
    model = models.WeaponProfScaling
    extra = 0


class WeaponProfBonusesInline(admin.StackedInline):
    model = models.WeaponProfBonuses
    extra = 0


class WeaponProfSubDiceInline(admin.TabularInline):
    model = models.WeaponProfSubDice
    extra = 0


class WeaponProfSubScalingInline(admin.TabularInline):
    model = models.WeaponProfSubScaling
    extra = 0


class WeaponProfSubBonusesInline(admin.StackedInline):
    model = models.WeaponProfSubBonuses
    extra = 0


class WeaponProfFeatAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'weapon_tree', 'level']
    list_display_links = ['id', 'name']
    search_fields = ['name', 'weapon_tree']
    inlines = [WeaponProfSubParentInline, WeaponProfSubExtendsInline,
               WeaponProfScalingInline, WeaponProfDiceInline, WeaponProfBonusesInline]


class WeaponProfSubAdmin(admin.ModelAdmin):
    inlines = [WeaponProfSubScalingInline,
               WeaponProfSubDiceInline, WeaponProfSubBonusesInline]


"""
Feats of Destiny
"""


class DestinyDiceInline(admin.TabularInline):
    model = models.DestinyDice
    extra = 0


class DestinyScalingInline(admin.TabularInline):
    model = models.DestinyScaling
    extra = 0


class DestinyBonusesInline(admin.StackedInline):
    model = models.DestinyBonuses
    extra = 0


class DestinyAdmin(admin.ModelAdmin):
    search_fields = ['name', 'description']
    inlines = [DestinyScalingInline, DestinyDiceInline, DestinyBonusesInline]


"""
Weapon Skills
"""


class WeaponSkillDiceInline(admin.TabularInline):
    model = models.WeaponSkillDice
    extra = 0


class WeaponSkillScalingInline(admin.TabularInline):
    model = models.WeaponSkillScaling
    extra = 0


class WeaponSkillBonusesInline(admin.StackedInline):
    model = models.WeaponSkillBonuses
    extra = 0


class WeaponSkillAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'usage_type', 'cost_fp']
    list_display_links = ['id', 'name']
    search_fields = ['name', 'usage_type']
    inlines = [WeaponSkillScalingInline,
               WeaponSkillDiceInline, WeaponSkillBonusesInline]


"""
Spells
"""


class SpellReqInline(admin.TabularInline):
    model = models.SpellRequirements
    extra = 0


class SpellDiceInline(admin.TabularInline):
    model = models.SpellDice
    extra = 0


class SpellBonusesInline(admin.StackedInline):
    model = models.SpellBonuses
    extra = 0

class SpellChargedInline(admin.TabularInline):
    model = models.SpellCharged
    extra = 0

class SpellAdmin(admin.ModelAdmin):
    readonly_fields = ("created_at", "updated_at", "created_by", "updated_by")
    list_display = ['id', 'name', 'category', 'ap', 'fp']
    list_display_links = ['id', 'name']
    search_fields = ['name', 'description']
    inlines = [SpellReqInline, SpellDiceInline, SpellBonusesInline, SpellChargedInline]


"""
Spirits
"""


class SpiritReqInline(admin.TabularInline):
    model = models.SpiritRequirements
    extra = 0


class SpiritDiceInline(admin.TabularInline):
    model = models.SpiritDice
    extra = 0


class SpiritAdmin(admin.ModelAdmin):
    readonly_fields = ("created_at", "updated_at", "created_by", "updated_by")
    list_display = ['id', 'name', 'tier', 'is_official']
    list_display_links = ['id', 'name']
    inlines = [SpiritReqInline, SpiritDiceInline]

"""
Items
"""


class ItemDiceInline(admin.TabularInline):
    model = models.ItemDice
    extra = 0


class ItemScalingInline(admin.TabularInline):
    model = models.ItemScaling
    extra = 0


class ItemBonusesInline(admin.StackedInline):
    model = models.ItemBonuses
    extra = 0


class ItemAdmin(admin.ModelAdmin):
    readonly_fields = ("created_at", "updated_at", "created_by", "updated_by")
    list_display = ['id', 'name', 'item_type',
                    'is_official', 'created_at', 'created_by']
    list_display_links = ['id', 'name']
    inlines = [ItemScalingInline, ItemDiceInline, ItemBonusesInline]


"""
Rings
"""


class RingDiceInline(admin.TabularInline):
    model = models.RingDice
    extra = 0


class RingScalingInline(admin.TabularInline):
    model = models.RingScaling
    extra = 0


class RingBonusesInline(admin.StackedInline):
    model = models.RingBonuses
    extra = 0


class RingAdmin(admin.ModelAdmin):
    readonly_fields = ("created_at", "updated_at", "created_by", "updated_by")
    list_display = ['id', 'name', 'tier', 'created_at', 'created_by']
    list_display_links = ['id', 'name']
    inlines = [RingScalingInline, RingDiceInline, RingBonusesInline]


"""
Artifact
"""


class ArtifactDiceInline(admin.TabularInline):
    model = models.ArtifactDice
    extra = 0


class ArtifactScalingInline(admin.TabularInline):
    model = models.ArtifactScaling
    extra = 0


class ArtifactBonusesInline(admin.StackedInline):
    model = models.ArtifactBonuses
    extra = 0


class ArtifactUpgradeInline(admin.TabularInline):
    model = models.ArtifactUpgrade
    extra = 0
    fields = ['name', 'visible', 'requirements_visible', 'unlock_requirements', 'description']
    show_change_link = True


class ArtifactAdmin(admin.ModelAdmin):
    readonly_fields = ("created_at", "updated_at", "created_by", "updated_by")
    list_display = ['id', 'name', 'created_at', 'created_by']
    list_display_links = ['id', 'name']
    search_fields = ['name', 'description']
    inlines = [ArtifactScalingInline,
               ArtifactDiceInline, ArtifactBonusesInline, ArtifactUpgradeInline]


"""
Armor
"""


class ArmorReqInline(admin.TabularInline):
    model = models.ArmorRequirements
    extra = 0


class ArmorBonusesInline(admin.StackedInline):
    model = models.ArmorBonuses
    extra = 0


class ArmorAdmin(admin.ModelAdmin):
    readonly_fields = ("created_at", "updated_at", "created_by", "updated_by")
    list_display = ['id', 'name', 'armor_type',
                    'is_official', 'created_at', 'created_by']
    list_display_links = ['id', 'name']
    inlines = [ArmorReqInline, ArmorBonusesInline]


"""
Weapon
"""


class WeaponDiceInline(admin.TabularInline):
    model = models.WeaponDice
    extra = 0


class WeaponScalingInline(admin.TabularInline):
    model = models.WeaponScaling
    extra = 0


class WeaponSpellScalingInline(admin.TabularInline):
    model = models.SpellScaling
    extra = 0


class WeaponReqInline(admin.TabularInline):
    model = models.WeaponRequirements
    extra = 0


class WeaponBonusesInline(admin.StackedInline):
    model = models.WeaponBonuses
    extra = 0


class WeaponAdmin(admin.ModelAdmin):
    readonly_fields = ("created_at", "updated_at", "created_by", "updated_by")
    list_display = ['id', 'name', 'weapon_type', 'second_type',
                    'is_official', 'created_at', 'created_by']
    list_display_links = ['id', 'name']
    inlines = [WeaponScalingInline, WeaponSpellScalingInline,
               WeaponReqInline, WeaponDiceInline, WeaponBonusesInline]


"""
Character Creation
"""


class BloodlineInline(admin.TabularInline):
    model = models.Bloodline
    extra = 0
    fields = ['name', 'description', 'has_unlock_requirement']


class BackgroundAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'starting_hp', 'vitality', 'endurance', 'strength', 'dexterity', 'attunement', 'intelligence', 'faith']
    list_display_links = ['id', 'name']
    readonly_fields = ['created_at', 'updated_at']


class LineageAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'subtitle']
    list_display_links = ['id', 'name']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [BloodlineInline]


class BloodlineAdmin(admin.ModelAdmin):
    list_display = ['id', 'lineage', 'name', 'has_unlock_requirement']
    list_display_links = ['id', 'name']
    list_filter = ['lineage', 'has_unlock_requirement']


class ArtifactUpgradeAdmin(admin.ModelAdmin):
    list_display = ['artifact', 'name', 'visible', 'requirements_visible', 'created_at']
    list_filter = ['visible', 'requirements_visible', 'artifact']
    search_fields = ['name', 'artifact__name', 'description']

    fieldsets = (
        ('Basic Information', {
            'fields': ('artifact', 'name')
        }),
        ('Visibility Controls', {
            'fields': ('visible', 'requirements_visible'),
            'description': 'Control what the player can see. "Visible" shows the upgrade exists. "Requirements Visible" shows what they need to unlock it.'
        }),
        ('Requirements', {
            'fields': ('unlock_requirements',)
        }),
        ('Effect Description', {
            'fields': ('description',)
        }),
        ('Influences', {
            'fields': (
                'influenced_spells',
                'influenced_weapon_prof_feats',
                'influenced_destiny_feats',
                'influenced_weapon_skills',
            ),
            'description': 'Select which game elements this upgrade affects. Use autocomplete to search.'
        }),
    )

    filter_horizontal = [
        'influenced_spells',
        'influenced_weapon_prof_feats',
        'influenced_destiny_feats',
        'influenced_weapon_skills',
    ]

    autocomplete_fields = ['artifact']


admin.site.register(models.Background, BackgroundAdmin)
admin.site.register(models.Lineage, LineageAdmin)
admin.site.register(models.Bloodline, BloodlineAdmin)
admin.site.register(models.UsageFormula)
admin.site.register(models.WeaponProfFeat, WeaponProfFeatAdmin)
admin.site.register(models.WeaponProfSubFeat, WeaponProfSubAdmin)
admin.site.register(models.DestinyFeat, DestinyAdmin)
admin.site.register(models.WeaponSkill, WeaponSkillAdmin)
admin.site.register(models.Spell, SpellAdmin)
admin.site.register(models.Spirit, SpiritAdmin)
admin.site.register(models.Item, ItemAdmin)
admin.site.register(models.Ring, RingAdmin)
admin.site.register(models.Artifact, ArtifactAdmin)
admin.site.register(models.ArtifactUpgrade, ArtifactUpgradeAdmin)
admin.site.register(models.Armor, ArmorAdmin)
admin.site.register(models.Weapon, WeaponAdmin)

