import datetime

from django.contrib.auth.models import User

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class ScalingValue(models.TextChoices):
    SS = "SS", _("SS")
    S = "S", _("S")
    A = "A", _("A")
    B = "B", _("B")
    C = "C", _("C")
    D = "D", _("D")
    E = "E", _("E")


class Stats(models.TextChoices):
    VITALITY = "VIT", _("Vitality")
    ENDURANCE = "END", _("Endurance")
    STRENGTH = "STR", _("Strength")
    DEXTERITY = "DEX", _("Dexterity")
    ATTUNEMENT = "ATT", _("Attunement")
    INTELLIGENCE = "INT", _("Intelligence")
    FAITH = "FAI", _("Faith")


class ScalingStat(models.TextChoices):
    STRENGTH = "STR", _("Strength")
    DEXTERITY = "DEX", _("Dexterity")
    INTELLIGENCE = "INT", _("Intelligence")
    FAITH = "FAI", _("Faith")


class ElementType(models.TextChoices):
    MAGIC = "MAGIC", _("Magic")
    FIRE = "FIRE", _("Fire")
    LIGHTNING = "LIGHTNING", _("Lightning")
    DARK = "DARK", _("Dark")


# class ElementTypePhys(models.TextChoices):
#     PHYSICAL = "PHYSICAL", _("Physical")
#     MAGIC = "MAGIC", _("Magic")
#     FIRE = "FIRE", _("Fire")
#     LIGHTNING = "LIGHTNING", _("Lightning")
#     DARK = "DARK", _("Dark")


class ElementTypeExpanded(models.TextChoices):
    PHYSICAL = "PHYSICAL", _("Physical")
    MAGIC = "MAGIC", _("Magic")
    FIRE = "FIRE", _("Fire")
    LIGHTNING = "LIGHTNING", _("Lightning")
    DARK = "DARK", _("Dark")
    TRUE = "TRUE", _("True Damage")
    VARYING = "VARYING", _("Varying Damage Type")
    REDUCE = "REDUCE", _("Damage Reduction")
    HEAL = "HEAL", _("HP Healing")
    FOCUS = "FOCUS", _("FP Regeneration")
    FROST = "FROST", _("Frostbite")
    BLEED = "BLEED", _("Bleed")
    POISON = "POISON", _("Poison")
    TOXIC = "TOXIC", _("Toxic")
    CURSE = "CURSE", _("Curse")
    POISE = "POISE", _("Poise")
    DURABILITY = "DURABILITY", _("Durability")


class WeaponProfTree(models.TextChoices):
    FIST = "FIST", _("Fist")
    DAGGER = "DAGGER", _("Dagger")
    STRAIGHT_THRUST = "STRAIGHT_THRUST", _("Straight Sword/Thrusting Sword")
    KATANA_CURVED = "KATANA_CURVED", _("Katana/Curved Sword")
    ULTRA_GREAT_SWORD = "ULTRA_GREAT_SWORD", _("Great Sword/Ultra Great Sword")
    GREAT_AXE = "GREAT_AXE", _("Axe/Great Axe")
    GREAT_HAMMER = "GREAT_HAMMER", _("Hammer/Great Hammer")
    TWINBLADE = "TWINBLADE", _("Twinblade")
    SPEAR = "SPEAR", _("Spear")
    HALBERD = "HALBERD", _("Halberd")
    REAPER = "REAPER", _("Reaper")
    WHIP = "WHIP", _("Whip")
    CROSS_BOW = "CROSS_BOW", _("Bow/Crossbow")
    GREAT_BOW_BALLISTA = "GREAT_BOW_BALLISTA", _("Great Bow/Ballista")
    GUN = "GUN", _("Gun Sidearm")
    SHIELD = "SHIELD", _("Shield")
    SORCERY = "SORCERY", _("Sorcery")
    MIRACLE = "MIRACLE", _("Miracle")
    PYROMANCY = "PYROMANCY", _("Pyromancy")
    HEX = "HEX", _("Hex")
    SPIRIT_SUMMONING = "SPIRIT_SUMMONING", _("Spirit Summoning")
    DUAL_WIELDING = "DUAL_WIELDING", _("Dual Wielding")


class UsageFormula(models.Model):
    class Modifier(models.TextChoices):
        NONE = "NON", _("None")
        LEVEL = "LVL", _("Level")
        VITALITY = "VIT", _("Vitality")
        ENDURANCE = "END", _("Endurance")
        STRENGTH = "STR", _("Strength")
        DEXTERITY = "DEX", _("Dexterity")
        ATTUNEMENT = "ATT", _("Attunement")
        INTELLIGENCE = "INT", _("Intelligence")
        FAITH = "FAI", _("Faith")
        ATHLETICS = "ATH", _("Athletics")
        ACROBATICS = "ACR", _("Acrobatics")
        PERCEPTION = "PER", _("Perception")
        FIRE_KEEPING = "FIR", _("Fire Keeping")
        SANITY = "SAN", _("Sanity")
        STEALTH = "STE", _("Stealth")
        PRECISION = "PRE", _("Precision")
        DIPLOMACY = "DIP", _("Diplomacy")
        STR_OR_DEX = "SOD", _("Strength Or Dexterity")
        STR_OR_INT = "SOI", _("Strength Or Intelligence")
        STR_OR_FAI = "SOF", _("Strength Or Faith")
        DEX_OR_INT = "DOI", _("Dexterity Or Intelligence")
        DEX_OR_FAI = "DOF", _("Dexterity Or Faith")
        END_OR_ATT = "EOA", _("Endurance Or Attunement")
        INT_OR_FAI = "IOF", _("Intelligence Or Faith")
    base_amount = models.IntegerField(default=0)
    divisor = models.IntegerField(default=1)
    multiplier = models.IntegerField(default=1)
    modifier = models.CharField(
        max_length=3,
        choices=Modifier.choices,
        default=Modifier.NONE,
    )

    def __str__(self) -> str:
        return f"{self.base_amount} + ( ({self.modifier} / {self.divisor}) * {self.multiplier})"


class WeaponProfFeat(models.Model):
    name = models.CharField(max_length=60)
    weapon_tree = models.CharField(
        max_length=18,
        choices=WeaponProfTree.choices
    )
    level = models.IntegerField(default=3)
    usage_formula = models.ForeignKey(
        UsageFormula, models.SET_NULL, blank=True, null=True, default=None)
    description = models.TextField(max_length=4096)

    def __str__(self) -> str:
        return f"{self.weapon_tree}: (Lv{self.level}) {self.name}"


class WeaponProfSubFeat(models.Model):
    parent = models.ForeignKey(
        WeaponProfFeat, models.CASCADE, related_name="sub_feat")
    extends = models.ForeignKey(
        WeaponProfFeat, models.CASCADE, related_name="extended")
    usage_formula = models.ForeignKey(
        UsageFormula, models.SET_NULL, blank=True, null=True, default=None)
    description = models.TextField(max_length=4096)

    def __str__(self) -> str:
        return f"{self.parent.name} -> {self.extends.name}"


class DestinyFeat(models.Model):
    name = models.CharField(max_length=60)
    cost = models.IntegerField(default=1)
    usage_formula = models.ForeignKey(
        UsageFormula, models.SET_NULL, blank=True, null=True, default=None)
    description = models.TextField(max_length=16384)

    def __str__(self) -> str:
        return f"{self.name}: (cost {self.cost})"


class WeaponSkill(models.Model):
    class UsageType(models.TextChoices):
        MELEE = "MELEE", _("Melee Only")
        RANGED = "RANGED", _("Ranged Only")
        BOTH = "BOTH", _("Melee and Ranged")
        CAST = "CAST", _("Casting Implements Only")
        MCAST = "MCAST", _("Melee and Casting Implements")
        RCAST = "RCAST", _("Ranged and Casting Implements")
        BCAST = "BCAST", _("Both and Casting Implements")
        STANCE = "STANCE", _("Power Stance")
    name = models.CharField(max_length=60)
    cost_fp = models.IntegerField(default=0)
    is_slow = models.BooleanField(default=False)
    usage_type = models.CharField(max_length=6, choices=UsageType.choices)
    description = models.TextField(max_length=1024)

    def __str__(self) -> str:
        return self.name


class SpellBase(models.Model):
    class Meta:
        abstract = True
    cast_time = models.CharField(max_length=200)
    ap = models.IntegerField(default=0)
    fp = models.IntegerField(default=0)
    range = models.CharField(max_length=200)
    duration = models.CharField(max_length=200)
    description = models.TextField(max_length=1024)

class Spell(SpellBase):
    class SpellType(models.TextChoices):
        SOUL_CRYSTAL = "SOUL_CRYSTAL", _("Soul/Crystal Sorcery")
        FROST = "FROST", _("Frost Sorcery")
        ASSASSIN_LIGHT = "ASSASSIN_LIGHT", _("Assassin/Light Sorcery")
        COSMIC = "COSMIC", _("Cosmic Sorcery")
        DARK = "DARK", _("Dark Hex")
        DEBUFF_HEX = "DEBUFF_HEX", _("Debuffing Hex")
        BLOOD = "BLOOD", _("Blood Hex")
        DEATH = "DEATH", _("Death Hex")
        TIME = "TIME", _("Time Magic")
        HEALING = "HEALING", _("Healing Miracle")
        LIGHTNING = "LIGHTNING", _("Lightning Miracle")
        BUFF_DEF_MIRACLE = "BUFF_DEF_MIRACLE", _(
            "Buffing and Defensive Miracle")
        FORCE = "FORCE", _("Force Miracle")
        FIRE = "FIRE", _("Fire Pyromancy")
        DRAGON = "DRAGON", _("Dragon Pyromancy")
        PESTILENCE = "PESTILENCE", _("Pestilence Pyromancy")
        BUFF_DEBUFF_PYRO = "BUFF_DEBUFF_PYRO", _(
            "Buffing and Debuffing Pyromancy")
        DARKFROST_BLACKFIRE = "DARKFROST_BLACKFIRE", _(
            "Darkfrost/Blackfire Hex")
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, models.DO_NOTHING, blank=True, null=True, related_name="spell_created_by")
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User, models.DO_NOTHING, blank=True, null=True, related_name="spell_updated_by")
    name = models.CharField(max_length=200)
    is_official = models.BooleanField(default=False)
    category = models.CharField(max_length=20, choices=SpellType.choices)
    is_slow = models.BooleanField(default=False)
    att_cost = models.IntegerField(default=1)
    def __str__(self) -> str:
        return f"{self.name} - {self.get_category_display()}"

class SpellCharged(SpellBase):
    base_spell = models.OneToOneField(
        Spell, on_delete=models.CASCADE, primary_key=True, related_name="charged")

    def __str__(self) -> str:
        return f"{self.base_spell.name} (Charged Version) - {self.base_spell.get_category_display()}"


class Item(models.Model):
    class ItemType(models.TextChoices):
        TOOL = "TOOL", _("Tool")
        AMMO = "AMMO", _("Ammunition")
        MATERIAL = "MATERIAL", _("Crafting Material")
        BOOK = "BOOK", _("Spell or Weapon Skill Book")
        MISC = "MISC", _("Miscellaneous")
    name = models.CharField(max_length=60)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, models.DO_NOTHING, blank=True, null=True, related_name="item_created_by")
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User, models.DO_NOTHING, blank=True, null=True, related_name="item_updated_by")
    is_official = models.BooleanField(default=False)
    item_type = models.CharField(
        max_length=8,
        choices=ItemType.choices
    )
    range = models.CharField(max_length=20, blank=True, default="")
    duration = models.CharField(max_length=20, blank=True, default="")
    description = models.TextField(max_length=2048)

    def __str__(self) -> str:
        return f"{self.name} ({self.item_type})"


class Ring(models.Model):
    name = models.CharField(max_length=60)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    created_by = models.ForeignKey(
        User, models.DO_NOTHING, blank=True, null=True, related_name="ring_created_by")
    updated_at = models.DateTimeField(auto_now=True, null=True)
    updated_by = models.ForeignKey(
        User, models.DO_NOTHING, blank=True, null=True, related_name="ring_updated_by")
    tier = models.IntegerField(default=1)
    usage_formula = models.ForeignKey(
        UsageFormula, models.SET_NULL, blank=True, null=True, default=None)
    description = models.TextField(max_length=2048)

    def __str__(self) -> str:
        return self.name


class Artifact(models.Model):
    name = models.CharField(max_length=60)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, models.DO_NOTHING, blank=True, null=True, related_name="artifact_created_by")
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User, models.DO_NOTHING, blank=True, null=True, related_name="artifact_updated_by")
    usage_formula = models.ForeignKey(
        UsageFormula, models.SET_NULL, blank=True, null=True, default=None)
    description = models.TextField(max_length=2048)

    def __str__(self) -> str:
        return self.name


class Armor(models.Model):
    class ArmorType(models.TextChoices):
        LIGHT = "LIGHT", _("Light")
        MEDIUM = "MEDIUM", _("Medium")
        HEAVY = "HEAVY", _("Heavy")
    name = models.CharField(max_length=60)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, models.DO_NOTHING, blank=True, null=True, related_name="armor_created_by")
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User, models.DO_NOTHING, blank=True, null=True, related_name="armor_updated_by")
    is_official = models.BooleanField(default=False)
    armor_type = models.CharField(
        max_length=6,
        choices=ArmorType.choices
    )

    usage_formula = models.ForeignKey(
        UsageFormula, models.SET_NULL, blank=True, null=True, default=None)

    description = models.TextField(max_length=512)
    durability = models.IntegerField(default=10)

    def __str__(self) -> str:
        return self.name


class Weapon(models.Model):
    class WeaponType(models.TextChoices):
        FIST = "FIST", _("Fist")
        DAGGER = "DAGGER", _("Dagger")
        STRAIGHT = "STRAIGHT", _("Straight Sword")
        THRUST = "THRUST", _("Thrusting Sword")
        KATANA = "KATANA", _("Katana")
        CURVED = "CURVED", _("Curved Sword")
        GREAT_SWORD = "GREAT_SWORD", _("Great Sword")
        ULTRA_GREAT_SWORD = "ULTRA_GREAT_SWORD", _("Ultra Great Sword")
        AXE = "AXE", _("Axe")
        GREAT_AXE = "GREAT_AXE", _("Great Axe")
        HAMMER = "HAMMER", _("Hammer")
        GREAT_HAMMER = "GREAT_HAMMER", _("Great Hammer")
        TWINBLADE = "TWINBLADE", _("Twinblade")
        SPEAR = "SPEAR", _("Spear")
        HALBERD = "HALBERD", _("Halberd")
        REAPER = "REAPER", _("Reaper")
        WHIP = "WHIP", _("Whip")
        CROSSBOW = "CROSSBOW", _("Crossbow")
        BOW = "BOW", _("Bow")
        GREAT_BOW = "GREAT_BOW", _("Great Bow")
        BALLISTA = "BALLISTA", _("Ballista")
        GUN = "GUN", _("Gun Sidearm")
        SHIELD = "SHIELD", _("Shield")
        GREAT_SHIELD = "GREAT_SHIELD", _("Great Shield")
        STAFF = "STAFF", _("Staff")
        TALISMAN = "TALISMAN", _("Talisman")
        PYRO = "PYRO", _("Pyromancy Flame")
        CRUCIBLE = "CRUCIBLE", _("Crucible")

    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, models.DO_NOTHING, blank=True, null=True, related_name="weapon_created_by")
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User, models.DO_NOTHING, blank=True, null=True, related_name="weapon_updated_by")
    is_official = models.BooleanField(default=False)

    is_trick = models.BooleanField(default=False)
    is_twin = models.BooleanField(default=False)
    weapon_type = models.CharField(max_length=20, choices=WeaponType.choices)
    second_type = models.CharField(
        max_length=20, choices=WeaponType.choices, blank=True, null=True, default=None)

    ap = models.IntegerField(default=3)
    skill_primary = models.ForeignKey(
        WeaponSkill, models.SET_NULL, blank=True, null=True, default=None)
    skill_secondary = models.ForeignKey(
        WeaponSkill, models.SET_NULL, blank=True, null=True, default=None, related_name="weapon_skill_secondary")

    usage_formula = models.ForeignKey(
        UsageFormula, models.SET_NULL, blank=True, null=True, default=None)

    description = models.TextField(max_length=512)
    durability = models.IntegerField(default=10)
    infusion = models.CharField(
        max_length=9, choices=ElementType.choices, blank=True, null=True, default=None)

    def __str__(self) -> str:
        return self.name


class SpellScaling(models.Model):
    class SpellStat(models.TextChoices):
        INTELLIGENCE = "INT", _("Intelligence")
        FAITH = "FAI", _("Faith")
    stat = models.CharField(max_length=3, choices=SpellStat.choices)
    requirement = models.IntegerField(default=0)
    value = models.CharField(max_length=2, choices=ScalingValue.choices)
    weapon = models.ForeignKey(
        Weapon, on_delete=models.CASCADE, related_name="spell_scaling")

    def __str__(self) -> str:
        return f"{self.value}-{self.stat} | Req: {self.requirement} "


class Scaling(models.Model):
    class Meta:
        abstract = True
    type = models.CharField(max_length=10, choices=ElementTypeExpanded.choices)
    stat = models.CharField(max_length=3, choices=Stats.choices)
    value = models.CharField(max_length=2, choices=ScalingValue.choices)

    def __str__(self) -> str:
        return f"{self.type}: {self.value}-{self.stat}"


class WeaponScaling(Scaling):
    class ScalingType(models.TextChoices):
        PHYSICAL = "PHYSICAL", _("Physical")
        MAGIC = "MAGIC", _("Magic")
        FIRE = "FIRE", _("Fire")
        LIGHTNING = "LIGHTNING", _("Lightning")
        DARK = "DARK", _("Dark")
        TONE = "TONE", _("Tier One Summon")
        TTWO = "TTWO", _("Tier Two Summon")
        TTHREE = "TTHREE", _("Tier Three Summon")
        TFOUR = "TFOUR", _("Tier Four Summon")
    type = models.CharField(max_length=9, choices=ScalingType.choices)
    stat = models.CharField(max_length=3, choices=ScalingStat.choices)
    weapon = models.ForeignKey(
        Weapon, on_delete=models.CASCADE, related_name="scaling")


class WeaponProfScaling(Scaling):
    weapon_prof = models.ForeignKey(
        WeaponProfFeat, on_delete=models.CASCADE, related_name="scaling")


class WeaponProfSubScaling(Scaling):
    weapon_prof = models.ForeignKey(
        WeaponProfSubFeat, on_delete=models.CASCADE, related_name="scaling")


class DestinyScaling(Scaling):
    destiny_feat = models.ForeignKey(
        DestinyFeat, on_delete=models.CASCADE, related_name="scaling")


class WeaponSkillScaling(Scaling):
    weapon_skill = models.ForeignKey(
        WeaponSkill, on_delete=models.CASCADE, related_name="scaling")


class RingScaling(Scaling):
    ring = models.ForeignKey(
        Ring, on_delete=models.CASCADE, related_name="scaling")


class ArtifactScaling(Scaling):
    artifact = models.ForeignKey(
        Artifact, on_delete=models.CASCADE, related_name="scaling")


class ItemScaling(Scaling):
    item = models.ForeignKey(
        Item, on_delete=models.CASCADE, related_name="scaling")


class Dice(models.Model):
    class Meta:
        abstract = True
    count = models.IntegerField(default=0)
    value = models.IntegerField(default=0)
    type = models.CharField(max_length=10, choices=ElementTypeExpanded.choices)

    def __str__(self) -> str:
        return f"{self.type} - {self.count}d{self.value}"


class WeaponDice(Dice):
    weapon = models.ForeignKey(
        Weapon, on_delete=models.CASCADE, related_name="dice")


class WeaponProfDice(Dice):
    weapon_prof = models.ForeignKey(
        WeaponProfFeat, on_delete=models.CASCADE, related_name="dice")


class WeaponProfSubDice(Dice):
    weapon_prof = models.ForeignKey(
        WeaponProfSubFeat, on_delete=models.CASCADE, related_name="dice")


class DestinyDice(Dice):
    destiny_feat = models.ForeignKey(
        DestinyFeat, on_delete=models.CASCADE, related_name="dice")


class WeaponSkillDice(Dice):
    weapon_skill = models.ForeignKey(
        WeaponSkill, on_delete=models.CASCADE, related_name="dice")
    
class SpellDice(Dice):
    spell = models.ForeignKey(
        Spell, on_delete=models.CASCADE, related_name="dice")
    
class SpellChargedDice(Dice):
    spell = models.ForeignKey(
        SpellCharged, on_delete=models.CASCADE, related_name="dice")


class RingDice(Dice):
    ring = models.ForeignKey(
        Ring, on_delete=models.CASCADE, related_name="dice")


class ArtifactDice(Dice):
    artifact = models.ForeignKey(
        Artifact, on_delete=models.CASCADE, related_name="dice")


class ItemDice(Dice):
    item = models.ForeignKey(
        Item, on_delete=models.CASCADE, related_name="dice")


class Requirements(models.Model):
    class Meta:
        abstract = True
    str = models.IntegerField(default=0)
    dex = models.IntegerField(default=0)
    int = models.IntegerField(default=0)
    fai = models.IntegerField(default=0)


class ArmorRequirements(Requirements):
    armor = models.OneToOneField(
        Armor, on_delete=models.CASCADE, primary_key=True, related_name="requirements")

    def __str__(self) -> str:
        return f"{self.armor.name} Requirements"


class WeaponRequirements(Requirements):
    weapon = models.OneToOneField(
        Weapon, on_delete=models.CASCADE, primary_key=True, related_name="requirements")

    def __str__(self) -> str:
        return f"{self.weapon.name} Requirements"
    
class SpellRequirements(models.Model):
    int = models.IntegerField(default=0)
    fai = models.IntegerField(default=0)
    spell = models.OneToOneField(
        Spell, on_delete=models.CASCADE, primary_key=True, related_name="requirements")

    def __str__(self) -> str:
        return f"{self.spell.name} Requirements"


class Bonuses(models.Model):
    class Meta:
        abstract = True

    class BonusType(models.TextChoices):
        MAX_HP = "MAX_HP", _("Maximum HP")
        MAX_AP = "MAX_AP", _("Maximum AP")
        MAX_FP = "MAX_FP", _("Maximum FP")
        VIT = "VIT", _("Vitality")
        END = "END", _("Endurance")
        STR = "STR", _("Strength")
        DEX = "DEX", _("Dexterity")
        ATT = "ATT", _("Attunement")
        INT = "INT", _("Intelligence")
        FAI = "FAI", _("Faith")
        ATH = "ATH", _("Athletics")
        ACR = "ACR", _("Acrobatics")
        PER = "PER", _("Perception")
        FIR = "FIR", _("Fire Keeping")
        SAN = "SAN", _("Sanity")
        STE = "STE", _("Stealth")
        PRE = "PRE", _("Precision")
        DIP = "DIP", _("Diplomacy")
        TIER_PHYSICAL = "TIER_PHYSICAL", _("Physical Resistance Tier")
        TIER_MAGIC = "TIER_MAGIC", _("Magic Resistance Tier")
        TIER_FIRE = "TIER_FIRE", _("Fire Resistance Tier")
        TIER_LIGHTNING = "TIER_LIGHTNING", _("Lightning Resistance Tier")
        TIER_DARK = "TIER_DARK", _("Dark Resistance Tier")
        FLAT_PHYSICAL = "FLAT_PHYSICAL", _("Physical Resistance Flat")
        FLAT_MAGIC = "FLAT_MAGIC", _("Magic Resistance Flat")
        FLAT_FIRE = "FLAT_FIRE", _("Fire Resistance Flat")
        FLAT_LIGHTNING = "FLAT_LIGHTNING", _("Lightning Resistance Flat")
        FLAT_DARK = "FLAT_DARK", _("Dark Resistance Flat")
        FLAT_PHYS_PER_TIER = "FLAT_PHYS_PER_TIER", _(
            "Flat Physical Resistance Per Tier")
        FLAT_PHYS_PER_COMBAT = "FLAT_PHYS_PER_COMBAT", _(
            "Flat Physical Resistance Once Per Combat")
        CURSE = "CURSE", _("Curse")
        FROST = "FROST", _("Frost")
        BLEED = "BLEED", _("Bleed")
        POISON = "POISON", _("Poison")
        TOXIC = "TOXIC", _("Toxic")
        POISE = "POISE", _("Poise")
        KNOW_MAGIC = "KNOW_MAGIC", _("Knowledge Magics")
        KNOW_HISTORY = "KNOW_HISTORY", _("Knowledge World History")
        KNOW_MONSTERS = "KNOW_MONSTERS", _("Knowledge Monsters")
        KNOW_COSMIC = "KNOW_COSMIC", _("Knowledge Cosmic")
        ATT_SLOTS = "ATT_SLOTS", _("Attunement Slots")
        FREE_MOVE = "FREE_MOVE", _("Free Movement")
        REGEN_HP = "REGEN_HP", _("HP Regeneration")
        REGEN_FP = "REGEN_FP", _("FP Regeneration")
        DODGE_DIST = "DODGE_DIST", _("Dodge Distance")
        DODGE_EXTRA = "DODGE_EXTRA", _("Extra Dodges")
        DODGE_PER_COMBAT = "DODGE_PER_COMBAT", _("Bonus Dodges Per Combat")
        MAX_INT = "MAX_INT", _("Maximum Intelligence")
        MAX_FAI = "MAX_FAI", _("Maximum Faith")
        MAX_FP_VIT_PLUS = "MAX_FP_VIT_PLUS", _("Vit Mod + Bonus To Max FP")
        MAX_HP_VIT_TIMES = "MAX_HP_VIT_TIMES", _(
            "Bonus + Bonus * Vit Mod To Max HP")
        ATH_SUCCESS = "ATH_SUCCESS", _("Auto Succeed Athletics Per Combat")
        VIT_ATH = "VIT_ATH", _("Vit Mod to Athletics")
        VIT_ACR = "VIT_ACR", _("Vit Mod to Acrobatics")
        VIT_PER = "VIT_PER", _("Vit Mod to Perception")
        VIT_FIR = "VIT_FIR", _("Vit Mod to Fire Keeping")
        VIT_SAN = "VIT_SAN", _("Vit Mod to Sanity")
        VIT_STE = "VIT_STE", _("Vit Mod to Stealth")
        VIT_PRE = "VIT_PRE", _("Vit Mod to Precision")
        VIT_DIP = "VIT_DIP", _("Vit Mod to Diplomacy")
    type = models.CharField(max_length=20, choices=BonusType.choices)
    value = models.IntegerField(default=0)


class WeaponProfBonuses(Bonuses):
    weapon_prof = models.ForeignKey(
        WeaponProfFeat, on_delete=models.CASCADE, related_name="bonuses")

    def __str__(self) -> str:
        return f"{self.weapon_prof.name} Bonuses"


class WeaponProfSubBonuses(Bonuses):
    weapon_prof = models.ForeignKey(
        WeaponProfSubFeat, on_delete=models.CASCADE, related_name="bonuses")


class DestinyBonuses(Bonuses):
    destiny_feat = models.ForeignKey(
        DestinyFeat, on_delete=models.CASCADE, related_name="bonuses")

    def __str__(self) -> str:
        return f"{self.destiny_feat.name} Bonuses"


class WeaponSkillBonuses(Bonuses):
    weapon_skill = models.ForeignKey(
        WeaponSkill, on_delete=models.CASCADE, related_name="bonuses")

    def __str__(self) -> str:
        return f"{self.weapon_skill.name} Bonuses"
    
class SpellBonuses(Bonuses):
    spell = models.ForeignKey(
        Spell, on_delete=models.CASCADE, related_name="bonuses")

    def __str__(self) -> str:
        return f"{self.spell.name} Bonuses"
    
class SpellChargedBonuses(Bonuses):
    spell = models.ForeignKey(
        SpellCharged, on_delete=models.CASCADE, related_name="bonuses")

    def __str__(self) -> str:
        return f"{self.spell.name} Bonuses"


class ItemBonuses(Bonuses):
    item = models.ForeignKey(
        Item, on_delete=models.CASCADE, related_name="bonuses")

    def __str__(self) -> str:
        return f"{self.ring.name} Bonuses"

class RingBonuses(Bonuses):
    ring = models.ForeignKey(
        Ring, on_delete=models.CASCADE, related_name="bonuses")

    def __str__(self) -> str:
        return f"{self.ring.name} Bonuses"


class ArtifactBonuses(Bonuses):
    artifact = models.ForeignKey(
        Artifact, on_delete=models.CASCADE, related_name="bonuses")

    def __str__(self) -> str:
        return f"{self.artifact.name} Bonuses"


class ArmorBonuses(Bonuses):
    armor = models.ForeignKey(
        Armor, on_delete=models.CASCADE, related_name="bonuses")
    is_innate = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.armor.name} Bonuses"


class WeaponBonuses(Bonuses):
    weapon = models.ForeignKey(
        Weapon, on_delete=models.CASCADE, related_name="bonuses")

    def __str__(self) -> str:
        return f"{self.weapon.name} Bonuses"


"""
class Character(models.Model):
    created_at = models.DateTimeField("date created")
    name = models.CharField(max_length=200)
    gender = models.CharField(max_length=200)
    race = models.CharField(max_length=200)
    background = models.CharField(max_length=200)
    undying = models.IntegerField(default=0)
    souls = models.IntegerField(default=0)
    level = models.IntegerField(default=0)
    
    UserInputValues = models.CharField(max_length=200)

    Inventory = models.CharField(max_length=200)
    Equipment = models.CharField(max_length=200)
    LearnedAttunedActions = models.CharField(max_length=200)
    AttunedActions = models.CharField(max_length=200)
    DestinyFeatSlots = models.IntegerField(default=0)
    DestinyFeats = models.CharField(max_length=200)
    CharacterStats = models.CharField(max_length=200)
    AvatarURL = models.CharField(max_length=200)

    def __str__(self) -> str:
        return self.name

"""
