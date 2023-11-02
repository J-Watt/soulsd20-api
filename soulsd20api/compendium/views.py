from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework import permissions
from compendium.serializers import (UserSerializer, GroupSerializer, UsageFormulaSerializer,
                                    WeaponProfFeatSerializer, DestinyFeatSerializer, ItemSerializer,
                                    RingSerializer, ArtifactSerializer, ArmorSerializer, WeaponSerializer)

from compendium.models import UsageFormula, WeaponProfFeat, DestinyFeat, Item, Ring, Artifact, Armor, Weapon


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


class UsageFormulaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows usage formulas to be viewed.
    """
    queryset = UsageFormula.objects.all()
    serializer_class = UsageFormulaSerializer


class WeaponProfFeatViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows Weapon Proficiency Feats to be viewed.
    """
    queryset = WeaponProfFeat.objects.all()
    serializer_class = WeaponProfFeatSerializer


class DestinyFeatViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows Feats of Destiny to be viewed.
    """
    queryset = DestinyFeat.objects.all()
    serializer_class = DestinyFeatSerializer


class ItemViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows Items to be viewed.
    """
    queryset = Item.objects.all()
    serializer_class = ItemSerializer


class RingViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows rings to be viewed.
    """
    queryset = Ring.objects.all()
    serializer_class = RingSerializer


class ArtifactViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows artifacts to be viewed.
    """
    queryset = Artifact.objects.all()
    serializer_class = ArtifactSerializer

class ArmorViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows armor to be viewed.
    """
    queryset = Armor.objects.all()
    serializer_class = ArmorSerializer

class WeaponViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows weapons to be viewed.
    """
    queryset = Weapon.objects.all()
    serializer_class = WeaponSerializer
