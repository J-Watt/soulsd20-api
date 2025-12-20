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


class WeaponSkillViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows WeaponSkills to be viewed.
    """
    queryset = WeaponSkill.objects.all()
    serializer_class = serializers.WeaponSkillSerializer

class SpellViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows Spells to be viewed.
    """
    queryset = Spell.objects.all()
    serializer_class = serializers.SpellSerializer

class SpiritViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows Spirits to be viewed.
    """
    queryset = Spirit.objects.all()
    serializer_class = serializers.SpiritSerializer


class ItemViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows Items to be viewed.
    """
    queryset = Item.objects.all()
    serializer_class = serializers.ItemSerializer


class RingViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows rings to be viewed.
    """
    queryset = Ring.objects.all()
    serializer_class = serializers.RingSerializer


class ArtifactViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows artifacts to be viewed.
    """
    queryset = Artifact.objects.all()
    serializer_class = serializers.ArtifactSerializer


class ArmorViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows armor to be viewed.
    """
    queryset = Armor.objects.all()
    serializer_class = serializers.ArmorSerializer


class WeaponViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows weapons to be viewed.
    """
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
