from django.contrib.auth.models import User, Group
from rest_framework import serializers
from compendium.models import (UsageFormula, WeaponProfFeat, DestinyFeat, Item, Ring, Artifact,
                               Armor, Weapon,
                               WeaponProfBonuses, DestinyFeatBonuses, RingBonuses, ArtifactBonuses,
                               ArmorBonuses, WeaponBonuses)

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


class WeaponProfBonusesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = WeaponProfBonuses
        fields = baseBonuses.copy()


class WeaponProfFeatSerializer(serializers.HyperlinkedModelSerializer):
    usage_formula = UsageFormulaSerializer()
    bonuses = WeaponProfBonusesSerializer()

    class Meta:
        model = WeaponProfFeat
        fields = ['id', 'name', 'weapon_tree', 'level',
                  'usage_formula', 'description', 'bonuses']


class DestinyBonusesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DestinyFeatBonuses
        fields = baseBonuses.copy()


class DestinyFeatSerializer(serializers.HyperlinkedModelSerializer):
    usage_formula = UsageFormulaSerializer()
    bonuses = DestinyBonusesSerializer()

    class Meta:
        model = DestinyFeat
        fields = ['id', 'name', 'cost',
                  'description', 'usage_formula', 'bonuses']


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
    usage_formula = UsageFormulaSerializer()
    bonuses = RingBonusesSerializer()

    class Meta:
        model = Ring
        fields = ['id', 'name', 'created_at', 'created_by',
                  'tier', 'usage_formula', 'description', 'bonuses']


class ArtifactBonusesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ArtifactBonuses
        fields = baseBonuses.copy()


class ArtifactSerializer(serializers.HyperlinkedModelSerializer):
    usage_formula = UsageFormulaSerializer()
    bonuses = ArtifactBonusesSerializer()

    class Meta:
        model = Artifact
        fields = ['id', 'name', 'created_at', 'created_by',
                  'usage_formula', 'description', 'bonuses']


class ArmorBonusesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ArmorBonuses
        fields = baseBonuses.copy()


class ArmorSerializer(serializers.HyperlinkedModelSerializer):
    usage_formula = UsageFormulaSerializer()
    bonuses = ArmorBonusesSerializer()

    class Meta:
        model = Armor
        fields = ['id', 'name', 'created_at', 'created_by', 'is_official',
                  'usage_formula', 'armor_type', 'description', 'durability', 'bonuses']


class WeaponBonusesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = WeaponBonuses
        fields = baseBonuses.copy()


class WeaponSerializer(serializers.HyperlinkedModelSerializer):
    usage_formula = UsageFormulaSerializer()
    bonuses = WeaponBonusesSerializer()

    class Meta:
        model = Weapon
        fields = ['id', 'name', 'created_at', 'created_by', 'is_official', 'is_trick', 'is_twin',
                  'weapon_type', 'second_type', 'ap', 'skill', 'second_skill', 'usage_formula',
                  'description', 'durability', 'infusion', 'bonuses']
