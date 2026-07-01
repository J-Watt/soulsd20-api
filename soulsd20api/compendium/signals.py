"""
Signals that bump compendium version numbers when items change.

Two version tracks:
 - CompendiumGlobalVersion (singleton, pk=1): bumps when any is_official item changes.
 - Campaign.compendium_version: bumps when a per-campaign custom item changes.

Clients call GET /api/compendium/versions/ to see both numbers and decide
which cached layers to refetch.

Design note (see Debugging_2026_06_29.md Batch 11 finding):
CampaignItemViewSet.partial_update always calls obj.save() on the parent BEFORE
clearing and recreating children. So post_save on top-level parents fires reliably
on every edit. Children (Dice, Scaling, Bonuses, etc.) do not need their own
signals; their parent's signal covers them.

The exceptions are ArtifactUpgrade and Bloodline, which can be edited
independently via the Django admin, so they get their own signals.
UsageFormula edits bump the global version conservatively because it can be
referenced by many items across many campaigns.
"""

from django.db.models import F
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import (
    Spell, Spirit, Item, Ring, Artifact, ArtifactUpgrade, Armor, Weapon,
    WeaponSkill, WeaponProfFeat, DestinyFeat,
    Background, Lineage, Bloodline, UsageFormula,
    CompendiumGlobalVersion,
)


def _bump_global():
    obj, _created = CompendiumGlobalVersion.objects.get_or_create(pk=1)
    CompendiumGlobalVersion.objects.filter(pk=1).update(version=F('version') + 1)


def _bump_campaign(campaign):
    if campaign is None:
        return
    from campaigns.models import Campaign
    Campaign.objects.filter(pk=campaign.pk).update(
        compendium_version=F('compendium_version') + 1
    )


def _bump_for_instance(instance):
    """Classify a top-level compendium instance and bump the right version."""
    campaign = getattr(instance, 'campaign', None)
    if campaign is not None:
        _bump_campaign(campaign)
        return
    if getattr(instance, 'is_official', True):
        _bump_global()
        return
    # is_official is False AND no campaign attached.
    # Conservative choice: bump global. This should be rare in practice.
    _bump_global()


# Top-level models that carry is_official (+ optionally campaign).
_TOP_LEVEL_WITH_FLAG = [
    Spell, Spirit, Item, Ring, Artifact, Armor, Weapon, WeaponSkill,
    WeaponProfFeat, DestinyFeat, Background, Lineage, Bloodline,
]

for _model in _TOP_LEVEL_WITH_FLAG:
    post_save.connect(
        lambda sender, instance, **kwargs: _bump_for_instance(instance),
        sender=_model,
        weak=False,
        dispatch_uid=f'sd20_compendium_version_save_{_model.__name__}',
    )
    post_delete.connect(
        lambda sender, instance, **kwargs: _bump_for_instance(instance),
        sender=_model,
        weak=False,
        dispatch_uid=f'sd20_compendium_version_delete_{_model.__name__}',
    )


@receiver(post_save, sender=ArtifactUpgrade, dispatch_uid='sd20_artifact_upgrade_save')
def _artifact_upgrade_saved(sender, instance, **kwargs):
    if instance.artifact is not None:
        _bump_for_instance(instance.artifact)


@receiver(post_delete, sender=ArtifactUpgrade, dispatch_uid='sd20_artifact_upgrade_delete')
def _artifact_upgrade_deleted(sender, instance, **kwargs):
    if instance.artifact is not None:
        _bump_for_instance(instance.artifact)


@receiver(post_save, sender=UsageFormula, dispatch_uid='sd20_usage_formula_save')
def _usage_formula_saved(sender, instance, **kwargs):
    _bump_global()


@receiver(post_delete, sender=UsageFormula, dispatch_uid='sd20_usage_formula_delete')
def _usage_formula_deleted(sender, instance, **kwargs):
    _bump_global()
