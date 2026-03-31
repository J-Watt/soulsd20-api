from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework import permissions
from . import serializers

from compendium.models import (UsageFormula, WeaponProfFeat, DestinyFeat, Item, Ring,
                               Artifact, Armor, Weapon, WeaponSkill, Spell, Spirit,
                               Background, Lineage, Bloodline)


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = serializers.UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = serializers.GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


class UsageFormulaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows usage formulas to be viewed.
    """
    queryset = UsageFormula.objects.all()
    serializer_class = serializers.UsageFormulaSerializer


class WeaponProfFeatViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows Weapon Proficiency Feats to be viewed.
    """
    queryset = WeaponProfFeat.objects.all()
    serializer_class = serializers.WeaponProfFeatSerializer


class DestinyFeatViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows Feats of Destiny to be viewed.
    """
    queryset = DestinyFeat.objects.all()
    serializer_class = serializers.DestinySerializer


class CampaignFilteredMixin:
    """
    Filters compendium items: official items + custom items from user's campaigns.
    """
    def get_queryset(self):
        from django.db.models import Q
        from campaigns.models import CampaignMembership

        qs = super().get_queryset()
        user = self.request.user

        if not user.is_authenticated or not hasattr(user, 'profile'):
            return qs.filter(is_official=True)

        # Get campaign IDs where user is GM or active member
        profile = user.profile
        from campaigns.models import Campaign
        gm_campaigns = Campaign.objects.filter(gm=profile).values_list('id', flat=True)
        member_campaigns = CampaignMembership.objects.filter(
            user=profile, status='active'
        ).values_list('campaign_id', flat=True)
        user_campaign_ids = set(gm_campaigns) | set(member_campaigns)

        # Official items + custom items from user's campaigns
        return qs.filter(
            Q(is_official=True) | Q(campaign_id__in=user_campaign_ids)
        )


class WeaponSkillViewSet(CampaignFilteredMixin, viewsets.ReadOnlyModelViewSet):
    """Weapon Skills: official + user's campaign custom weapon skills."""
    queryset = WeaponSkill.objects.all()
    serializer_class = serializers.WeaponSkillSerializer

class SpellViewSet(CampaignFilteredMixin, viewsets.ReadOnlyModelViewSet):
    """Spells: official + user's campaign custom spells."""
    queryset = Spell.objects.all()
    serializer_class = serializers.SpellSerializer

class SpiritViewSet(CampaignFilteredMixin, viewsets.ReadOnlyModelViewSet):
    """Spirits: official + user's campaign custom spirits."""
    queryset = Spirit.objects.all()
    serializer_class = serializers.SpiritSerializer


class ItemViewSet(CampaignFilteredMixin, viewsets.ReadOnlyModelViewSet):
    """Items: official + user's campaign custom items."""
    queryset = Item.objects.all()
    serializer_class = serializers.ItemSerializer


class RingViewSet(CampaignFilteredMixin, viewsets.ReadOnlyModelViewSet):
    """Rings: official + user's campaign custom rings."""
    queryset = Ring.objects.all()
    serializer_class = serializers.RingSerializer


class ArtifactViewSet(CampaignFilteredMixin, viewsets.ReadOnlyModelViewSet):
    """Artifacts: official + user's campaign custom artifacts."""
    queryset = Artifact.objects.all()
    serializer_class = serializers.ArtifactSerializer


class ArmorViewSet(CampaignFilteredMixin, viewsets.ReadOnlyModelViewSet):
    """Armor: official + user's campaign custom armor."""
    queryset = Armor.objects.all()
    serializer_class = serializers.ArmorSerializer


class WeaponViewSet(CampaignFilteredMixin, viewsets.ReadOnlyModelViewSet):
    """Weapons: official + user's campaign custom weapons."""
    queryset = Weapon.objects.all()
    serializer_class = serializers.WeaponSerializer


class BackgroundViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only endpoint for character starting backgrounds.
    Returns all 15 backgrounds with HP and base stats.
    """
    queryset = Background.objects.all()
    serializer_class = serializers.BackgroundSerializer


class LineageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only endpoint for character lineages (races).
    Returns all 11 lineages with nested bloodline variants.
    """
    queryset = Lineage.objects.prefetch_related('bloodlines').all()
    serializer_class = serializers.LineageSerializer


class BloodlineViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only endpoint for bloodline variants.
    Returns all 29 bloodlines across all lineages.
    """
    queryset = Bloodline.objects.select_related('lineage').all()
    serializer_class = serializers.BloodlineSerializer
