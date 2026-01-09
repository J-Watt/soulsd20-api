from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework import permissions
from . import serializers
from . import models


class UserViewSet(viewsets.ReadOnlyModelViewSet):
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
    queryset = models.UsageFormula.objects.all()
    serializer_class = serializers.UsageFormulaSerializer

class LineageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows Lineages to be viewed.
    """
    queryset = models.Lineage.objects.all()
    serializer_class = serializers.LineageSerializer

class BackgroundViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows Backgrounds to be viewed.
    """
    queryset = models.Background.objects.all()
    serializer_class = serializers.BackgroundSerializer

class CampaignViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows Campaigns to be viewed.
    """
    queryset = models.Campaign.objects.all()
    serializer_class = serializers.CampaignSerializer

class CharacterViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows Characters to be viewed.
    """
    queryset = models.Character.objects.all()
    serializer_class = serializers.CharacterSerializer

class WeaponProfFeatViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows Weapon Proficiency Feats to be viewed.
    """
    queryset = models.WeaponProfFeat.objects.all()
    serializer_class = serializers.WeaponProfFeatSerializer


class DestinyFeatViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows Feats of Destiny to be viewed.
    """
    queryset = models.DestinyFeat.objects.all()
    serializer_class = serializers.DestinySerializer


class WeaponSkillViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows WeaponSkills to be viewed.
    """
    queryset = models.WeaponSkill.objects.all()
    serializer_class = serializers.WeaponSkillSerializer

class SpellViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows Spells to be viewed.
    """
    queryset = models.Spell.objects.all()
    serializer_class = serializers.SpellSerializer

class SpiritViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows Spirits to be viewed.
    """
    queryset = models.Spirit.objects.all()
    serializer_class = serializers.SpiritSerializer


class ItemViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows Items to be viewed.
    """
    queryset = models.Item.objects.all()
    serializer_class = serializers.ItemSerializer


class RingViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows rings to be viewed.
    """
    queryset = models.Ring.objects.all()
    serializer_class = serializers.RingSerializer


class ArtifactViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows artifacts to be viewed.
    """
    queryset = models.Artifact.objects.all()
    serializer_class = serializers.ArtifactSerializer


class ArmorViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows armor to be viewed.
    """
    queryset = models.Armor.objects.all()
    serializer_class = serializers.ArmorSerializer


class WeaponViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows weapons to be viewed.
    """
    queryset = models.Weapon.objects.all()
    serializer_class = serializers.WeaponSerializer
