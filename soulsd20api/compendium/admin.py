from django.contrib import admin

from . import models

class RingBonusesInline(admin.StackedInline):
    model = models.RingBonuses

class RingAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'tier', 'created_at', 'created_by']
    list_display_links = ['id', 'name']
    inlines = [RingBonusesInline]

admin.site.register(models.UsageFormula)
admin.site.register(models.WeaponProfFeat)
admin.site.register(models.DestinyFeat)
admin.site.register(models.Item)
admin.site.register(models.Ring, RingAdmin)
admin.site.register(models.Artifact)
admin.site.register(models.Armor)
admin.site.register(models.Weapon)

# admin.site.register(models.WeaponProfBonuses)
# admin.site.register(models.DestinyFeatBonuses)
# admin.site.register(models.RingBonuses)
# admin.site.register(models.ArtifactBonuses)
