from django.contrib.auth.models import User, Group
from rest_framework import serializers
from . import models


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
        fields = ['type', 'value']


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
        fields = ['type', 'value']


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
    bonuses = WeaponProfSubBonusesSerializer(many=True)
    scaling = WeaponProfSubScalingSerializer(many=True)
    dice = WeaponProfSubDiceSerializer(many=True)

    class Meta:
        model = models.WeaponProfSubFeat
        fields = ['extends', 'usage_formula',
                  'description', 'scaling', 'dice', 'bonuses']


class WeaponProfFeatSerializer(serializers.HyperlinkedModelSerializer):
    usage_formula = UsageFormulaSerializer()
    bonuses = WeaponProfBonusesSerializer(many=True)
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
        fields = ['type', 'value']


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
    bonuses = DestinyBonusesSerializer(many=True)
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
        fields = ['type', 'value']


class WeaponSkillScalingSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.WeaponSkillScaling
        fields = ['type', 'stat', 'value']


class WeaponSkillDiceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.WeaponSkillDice
        fields = ['type', 'count', 'value']


class WeaponSkillSerializer(serializers.HyperlinkedModelSerializer):
    bonuses = WeaponSkillBonusesSerializer(many=True)
    scaling = WeaponSkillScalingSerializer(many=True)
    dice = WeaponSkillDiceSerializer(many=True)

    class Meta:
        model = models.WeaponSkill
        fields = ['id', 'name', 'cost_fp', 'is_slow', 'usage_type',
                  'description', 'scaling', 'dice', 'bonuses']


"""
Spell
"""


class SpellReqSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.SpellRequirements
        fields = ['int', 'fai']


class SpellBonusesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.SpellBonuses
        fields = ['type', 'value']


class SpellDiceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.SpellDice
        fields = ['type', 'count', 'value']


class SpellChargedBonusesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.SpellChargedBonuses
        fields = ['type', 'value']


class SpellChargedDiceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.SpellChargedDice
        fields = ['type', 'count', 'value']


class SpellChargedSerializer(serializers.HyperlinkedModelSerializer):
    bonuses = SpellBonusesSerializer(many=True)
    dice = SpellDiceSerializer(many=True)

    class Meta:
        model = models.SpellCharged
        fields = ['cast_time', 'ap', 'fp', 'range', 'duration', 'description', 'dice', 'bonuses']

class SpellSerializer(serializers.HyperlinkedModelSerializer):
    requirements = SpellReqSerializer()
    bonuses = SpellBonusesSerializer(many=True)
    dice = SpellDiceSerializer(many=True)
    charged = SpellChargedSerializer()

    class Meta:
        model = models.Spell
        fields = ['id', 'name', 'cast_time', 'ap', 'fp', 'range', 'duration', 'description', 'is_official',
                  'category', 'is_slow', 'att_cost', 'requirements', 'dice', 'bonuses', 'charged']


"""
Spirit
"""


class SpiritReqSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.SpiritRequirements
        fields = ['int', 'fai']


class SpiritDiceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.SpiritDice
        fields = ['type', 'count', 'value']


class SpiritSerializer(serializers.HyperlinkedModelSerializer):
    requirements = SpiritReqSerializer()
    dice = SpiritDiceSerializer(many=True)

    class Meta:
        model = models.Spell
        fields = ['id', 'name', 'created_at', 'created_by', 'is_official', 'tier', 'creature', 'size', 'range', 'condition', 'description', 'requirements',
                  'dice']


"""
Item
"""


class ItemBonusesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.ItemBonuses
        fields = ['type', 'value']


class ItemScalingSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.ItemScaling
        fields = ['type', 'stat', 'value']


class ItemDiceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.ItemDice
        fields = ['type', 'count', 'value']


class ItemSerializer(serializers.HyperlinkedModelSerializer):
    bonuses = ItemBonusesSerializer(many=True)
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
        fields = ['type', 'value']


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
    bonuses = RingBonusesSerializer(many=True)
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
        fields = ['type', 'value']


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
    bonuses = ArtifactBonusesSerializer(many=True)
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
        fields = ['type', 'value']


class ArmorReqSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.ArmorRequirements
        fields = ['str', 'dex', 'int', 'fai']


class ArmorSerializer(serializers.HyperlinkedModelSerializer):
    usage_formula = UsageFormulaSerializer()
    bonuses = ArmorBonusesSerializer(many=True)
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
        fields = ['type', 'value']


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
    bonuses = WeaponBonusesSerializer(many=True)
    scaling = WeaponScalingSerializer(many=True)
    spell_scaling = SpellScalingSerializer(many=True)
    dice = WeaponDiceSerializer(many=True)
    requirements = WeaponReqSerializer()

    class Meta:
        model = models.Weapon
        fields = ['id', 'name', 'created_at', 'created_by', 'is_official', 'is_trick', 'is_twin', 'weapon_type', 'second_type', 'ap', 'skill_primary',
                  'skill_secondary', 'usage_formula', 'description', 'durability', 'infusion', 'requirements', 'scaling', 'spell_scaling', 'dice', 'bonuses']
