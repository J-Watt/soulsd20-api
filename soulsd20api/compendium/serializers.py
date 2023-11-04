from django.contrib.auth.models import User, Group
from rest_framework import serializers
from . import models

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
        model = models.UsageFormula
        fields = ['id', 'base_amount', 'divisor', 'multiplier', 'modifier']


"""
Weapon Proficiency Feats
"""


class WeaponProfBonusesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.WeaponProfBonuses
        fields = baseBonuses.copy()


class WeaponProfScalingSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.WeaponProfScaling
        fields = ['type', 'stat', 'value']


class WeaponProfDiceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.WeaponProfDice
        fields = ['type', 'count', 'value']


class WeaponProfSubBonusesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.WeaponProfSubBonuses
        fields = baseBonuses.copy()


class WeaponProfSubScalingSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.WeaponProfSubScaling
        fields = ['type', 'stat', 'value']


class WeaponProfSubDiceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.WeaponProfSubDice
        fields = ['type', 'count', 'value']


class WeaponProfSubSerializer(serializers.HyperlinkedModelSerializer):
    usage_formula = UsageFormulaSerializer()
    bonuses = WeaponProfSubBonusesSerializer()
    scaling = WeaponProfSubScalingSerializer(many=True)
    dice = WeaponProfSubDiceSerializer(many=True)

    class Meta:
        model = models.WeaponProfSubFeat
        fields = ['extends', 'usage_formula',
                  'description', 'scaling', 'dice', 'bonuses']


class WeaponProfFeatSerializer(serializers.HyperlinkedModelSerializer):
    usage_formula = UsageFormulaSerializer()
    bonuses = WeaponProfBonusesSerializer()
    scaling = WeaponProfScalingSerializer(many=True)
    dice = WeaponProfDiceSerializer(many=True)
    sub_feat = WeaponProfSubSerializer(many=True)

    class Meta:
        model = models.WeaponProfFeat
        fields = ['id', 'name', 'weapon_tree', 'level',
                  'usage_formula', 'description', 'sub_feat', 'scaling', 'dice', 'bonuses']


"""
Feats of Destiny
"""


class DestinyBonusesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.DestinyBonuses
        fields = baseBonuses.copy()


class DestinyScalingSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.DestinyScaling
        fields = ['type', 'stat', 'value']


class DestinyDiceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.DestinyDice
        fields = ['type', 'count', 'value']


class DestinySerializer(serializers.HyperlinkedModelSerializer):
    usage_formula = UsageFormulaSerializer()
    bonuses = DestinyBonusesSerializer()
    scaling = DestinyScalingSerializer(many=True)
    dice = DestinyDiceSerializer(many=True)

    class Meta:
        model = models.DestinyFeat
        fields = ['id', 'name', 'cost', 'usage_formula',
                  'description', 'scaling', 'dice', 'bonuses']


"""
Weapon Skill
"""


class WeaponSkillBonusesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.WeaponSkillBonuses
        fields = baseBonuses.copy()


class WeaponSkillScalingSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.WeaponSkillScaling
        fields = ['type', 'stat', 'value']


class WeaponSkillDiceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.WeaponSkillDice
        fields = ['type', 'count', 'value']


class WeaponSkillSerializer(serializers.HyperlinkedModelSerializer):
    bonuses = WeaponSkillBonusesSerializer()
    scaling = WeaponSkillScalingSerializer(many=True)
    dice = WeaponSkillDiceSerializer(many=True)

    class Meta:
        model = models.WeaponSkill
        fields = ['id', 'name', 'cost_fp', 'is_slow', 'usage_type',
                  'description', 'scaling', 'dice', 'bonuses']


"""
Item
"""


class ItemBonusesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.ItemBonuses
        fields = baseBonuses.copy()


class ItemScalingSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.ItemScaling
        fields = ['type', 'stat', 'value']


class ItemDiceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.ItemDice
        fields = ['type', 'count', 'value']


class ItemSerializer(serializers.HyperlinkedModelSerializer):
    bonuses = ItemBonusesSerializer()
    scaling = ItemScalingSerializer(many=True)
    dice = ItemDiceSerializer(many=True)

    class Meta:
        model = models.Item
        fields = ['id', 'name', 'created_at', 'created_by', 'is_official', 'item_type',
                  'range', 'duration', 'description', 'scaling', 'dice', 'bonuses']


"""
Ring
"""


class RingBonusesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.RingBonuses
        fields = baseBonuses.copy()


class RingScalingSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.RingScaling
        fields = ['type', 'stat', 'value']


class RingDiceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.RingDice
        fields = ['type', 'count', 'value']


class RingSerializer(serializers.HyperlinkedModelSerializer):
    usage_formula = UsageFormulaSerializer()
    bonuses = RingBonusesSerializer()
    scaling = RingScalingSerializer(many=True)
    dice = RingDiceSerializer(many=True)

    class Meta:
        model = models.Ring
        fields = ['id', 'name', 'created_at', 'created_by', 'tier',
                  'usage_formula', 'description', 'scaling', 'dice', 'bonuses']


"""
Artifact
"""


class ArtifactBonusesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.ArtifactBonuses
        fields = baseBonuses.copy()


class ArtifactScalingSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.ArtifactScaling
        fields = ['type', 'stat', 'value']


class ArtifactDiceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.ArtifactDice
        fields = ['type', 'count', 'value']


class ArtifactSerializer(serializers.HyperlinkedModelSerializer):
    usage_formula = UsageFormulaSerializer()
    bonuses = ArtifactBonusesSerializer()
    scaling = ArtifactScalingSerializer(many=True)
    dice = ArtifactDiceSerializer(many=True)

    class Meta:
        model = models.Artifact
        fields = ['id', 'name', 'created_at', 'created_by',
                  'usage_formula', 'description', 'scaling', 'dice', 'bonuses']


"""
Armor
"""


class ArmorBonusesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.ArmorBonuses
        fields = baseBonuses.copy()


class ArmorReqSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.ArmorRequirements
        fields = ['str', 'dex', 'int', 'fai']


class ArmorSerializer(serializers.HyperlinkedModelSerializer):
    usage_formula = UsageFormulaSerializer()
    bonuses = ArmorBonusesSerializer()
    requirements = ArmorReqSerializer()

    class Meta:
        model = models.Armor
        fields = ['id', 'name', 'created_at', 'created_by', 'is_official',
                  'armor_type', 'usage_formula', 'description', 'requirements', 'bonuses']


"""
Weapon
"""


class WeaponBonusesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.WeaponBonuses
        fields = baseBonuses.copy()


class WeaponScalingSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.WeaponScaling
        fields = ['type', 'stat', 'value']


class SpellScalingSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.SpellScaling
        fields = ['stat', 'requirement', 'value']


class WeaponDiceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.WeaponDice
        fields = ['type', 'count', 'value']


class WeaponReqSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.WeaponRequirements
        fields = ['str', 'dex', 'int', 'fai']


class WeaponSerializer(serializers.HyperlinkedModelSerializer):
    usage_formula = UsageFormulaSerializer()
    bonuses = WeaponBonusesSerializer()
    scaling = WeaponScalingSerializer(many=True)
    spell_scaling = SpellScalingSerializer(many=True)
    dice = WeaponDiceSerializer(many=True)
    requirements = WeaponReqSerializer()

    class Meta:
        model = models.Weapon
        fields = ['id', 'name', 'created_at', 'created_by', 'is_official', 'is_trick', 'is_twin', 'weapon_type', 'second_type', 'ap', 'skill',
                  'second_skill', 'usage_formula', 'description', 'durability', 'infusion', 'requirements', 'scaling', 'spell_scaling', 'dice', 'bonuses']
