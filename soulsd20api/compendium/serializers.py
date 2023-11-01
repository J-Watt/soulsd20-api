from django.contrib.auth.models import User, Group
from rest_framework import serializers
from compendium.models import (UsageFormula, WeaponProfFeat, DestinyFeat, Item, Ring, Artifact,
                               RingBonuses)

baseBonuses = ['max_hp', 'max_fp', 'max_ap', 'attunement_slots', 'free_movement', 'vitality',
               'endurance', 'strength', 'dexterity', 'attunement', 'intelligence', 'faith',
               'athletics', 'acrobatics', 'perception', 'firekeeping', 'sanity', 'stealth',
               'precision', 'diplomacy', 'knowledge_magics', 'knowledge_history',
               'knowledge_monsters', 'knowledge_cosmic', 'resist_physical', 'resist_magic',
               'resist_fire', 'resist_lightning', 'resist_dark', 'flat_physical', 'flat_magic',
               'flat_fire', 'flat_lightning', 'flat_dark', 'curse', 'frost', 'bleed', 'poison',
               'toxic', 'poise']


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']


class UsageFormulaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UsageFormula
        fields = ['id', 'base_amount', 'divisor', 'multiplier', 'modifier']


class WeaponProfFeatSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = WeaponProfFeat
        fields = ['id', 'name', 'level', 'description',
                  'usage_formula', 'weapon_tree']


class DestinyFeatSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DestinyFeat
        fields = ['id', 'name', 'cost', 'description', 'usage_formula']


class ItemSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'name', 'created_at', 'created_by',
                  'editable', 'item_type', 'description']


class RingBonusesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = RingBonuses
        fields = baseBonuses.copy()


class RingSerializer(serializers.HyperlinkedModelSerializer):
    bonuses = RingBonusesSerializer()

    class Meta:
        model = Ring
        fields = ['id', 'name', 'created_at', 'created_by',
                  'tier', 'description', 'bonuses']


class ArtifactSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Artifact
        fields = ['id', 'name', 'created_at', 'created_by', 'description']
