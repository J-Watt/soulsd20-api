import datetime

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


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
    class WeaponProfTree(models.TextChoices):
        FIST = "FIST", _("Fist")
        DAGGER = "DAGGER", _("Dagger")
        STRAIGHT_THRUST = "STRAIGHT_THRUST", _(
            "Straight Sword/Thrusting Sword")
        KATANA_CURVED = "KATANA_CURVED", _("Katana/Curved Sword")
        ULTRA_GREAT_SWORD = "ULTRA_GREAT_SWORD", _(
            "Great Sword/Ultra Great Sword")
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
    name = models.CharField(max_length=60)
    cost_fp = models.IntegerField(default=0)
    is_slow = models.BooleanField(default=False)
    usage_type = models.CharField(max_length=6, choices=UsageType.choices)
    description = models.TextField(max_length=1024)

    def __str__(self) -> str:
        return self.name


class Item(models.Model):
    class ItemType(models.TextChoices):
        TOOL = "TOOL", _("Tool")
        AMMO = "AMMO", _("Ammunition")
        MATERIAL = "MATERIAL", _("Crafting Material")
        BOOK = "BOOK", _("Spell or Weapon Skill Book")
        MISC = "MISC", _("Miscellaneous")
    name = models.CharField(max_length=60)
    created_at = models.DateTimeField("date created")
    created_by = models.CharField(max_length=200)
    is_official = models.BooleanField(default=False)
    item_type = models.CharField(
        max_length=8,
        choices=ItemType.choices
    )
    description = models.TextField(max_length=2048)

    def __str__(self) -> str:
        return f"{self.name} ({self.item_type})"


class Ring(models.Model):
    name = models.CharField(max_length=60)
    created_at = models.DateTimeField("date created")
    created_by = models.CharField(max_length=200)
    tier = models.IntegerField(default=1)
    usage_formula = models.ForeignKey(
        UsageFormula, models.SET_NULL, blank=True, null=True, default=None)
    description = models.TextField(max_length=2048)

    def __str__(self) -> str:
        return self.name


class Artifact(models.Model):
    name = models.CharField(max_length=60)
    created_at = models.DateTimeField("date created")
    created_by = models.CharField(max_length=200)
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
    created_at = models.DateTimeField("date created")
    created_by = models.CharField(max_length=200)
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

    class ElementType(models.TextChoices):
        MAGIC = "MAGIC", _("Magic")
        FIRE = "FIRE", _("Fire")
        LIGHTNING = "LIGHTNING", _("Lightning")
        DARK = "DARK", _("Dark")

    name = models.CharField(max_length=200)
    created_at = models.DateTimeField("date created")
    created_by = models.CharField(max_length=200)
    is_official = models.BooleanField(default=False)

    is_trick = models.BooleanField(default=False)
    is_twin = models.BooleanField(default=False)
    weapon_type = models.CharField(max_length=20, choices=WeaponType.choices)
    second_type = models.CharField(
        max_length=20, choices=WeaponType.choices, blank=True, null=True, default=None)

    ap = models.IntegerField(default=3)
    skill = models.ForeignKey(
        WeaponSkill, models.SET_NULL, blank=True, null=True, default=None)
    second_skill = models.ForeignKey(
        WeaponSkill, models.SET_NULL, blank=True, null=True, default=None, related_name="SecondWeaponSkill")

    usage_formula = models.ForeignKey(
        UsageFormula, models.SET_NULL, blank=True, null=True, default=None)

    description = models.TextField(max_length=512)
    durability = models.IntegerField(default=10)
    infusion = models.CharField(
        max_length=9, choices=ElementType.choices, blank=True, null=True, default=None)

    def __str__(self) -> str:
        return self.name


class Damage(models.Model):
    class Meta:
        abstract = True
    die_count_phys = models.IntegerField(default=0)
    die_value_phys = models.IntegerField(default=0)
    die_count_magic = models.IntegerField(default=0)
    die_value_magic = models.IntegerField(default=0)
    die_count_fire = models.IntegerField(default=0)
    die_value_fire = models.IntegerField(default=0)
    die_count_lightning = models.IntegerField(default=0)
    die_value_lightning = models.IntegerField(default=0)
    die_count_dark = models.IntegerField(default=0)
    die_value_dark = models.IntegerField(default=0)
    die_count_frost = models.IntegerField(default=0)
    die_value_frost = models.IntegerField(default=0)
    die_count_bleed = models.IntegerField(default=0)
    die_value_bleed = models.IntegerField(default=0)
    die_count_poison = models.IntegerField(default=0)
    die_value_poison = models.IntegerField(default=0)
    die_count_toxic = models.IntegerField(default=0)
    die_value_toxic = models.IntegerField(default=0)


class WeaponDamage(Damage):
    class Scaling(models.TextChoices):
        SS = "SS", _("SS")
        S = "S", _("S")
        A = "A", _("A")
        B = "B", _("B")
        C = "C", _("C")
        D = "D", _("D")
        E = "E", _("E")

    weapon = models.OneToOneField(
        Weapon, on_delete=models.CASCADE, primary_key=True, related_name="damage")

    scaling_phys_str = models.CharField(
        max_length=2, choices=Scaling.choices, default=None, blank=True, null=True)
    scaling_phys_dex = models.CharField(
        max_length=2, choices=Scaling.choices, default=None, blank=True, null=True)
    scaling_phys_int = models.CharField(
        max_length=2, choices=Scaling.choices, default=None, blank=True, null=True)
    scaling_phys_fai = models.CharField(
        max_length=2, choices=Scaling.choices, default=None, blank=True, null=True)
    scaling_element_str = models.CharField(
        max_length=2, choices=Scaling.choices, default=None, blank=True, null=True)
    scaling_element_dex = models.CharField(
        max_length=2, choices=Scaling.choices, default=None, blank=True, null=True)
    scaling_element_int = models.CharField(
        max_length=2, choices=Scaling.choices, default=None, blank=True, null=True)
    scaling_element_fai = models.CharField(
        max_length=2, choices=Scaling.choices, default=None, blank=True, null=True)

    spell_int_SS = models.IntegerField(default=None, blank=True, null=True)
    spell_int_S = models.IntegerField(default=None, blank=True, null=True)
    spell_int_A = models.IntegerField(default=None, blank=True, null=True)
    spell_int_B = models.IntegerField(default=None, blank=True, null=True)
    spell_int_C = models.IntegerField(default=None, blank=True, null=True)
    spell_int_D = models.IntegerField(default=None, blank=True, null=True)
    spell_int_E = models.IntegerField(default=None, blank=True, null=True)
    spell_fai_SS = models.IntegerField(default=None, blank=True, null=True)
    spell_fai_S = models.IntegerField(default=None, blank=True, null=True)
    spell_fai_A = models.IntegerField(default=None, blank=True, null=True)
    spell_fai_B = models.IntegerField(default=None, blank=True, null=True)
    spell_fai_C = models.IntegerField(default=None, blank=True, null=True)
    spell_fai_D = models.IntegerField(default=None, blank=True, null=True)
    spell_fai_E = models.IntegerField(default=None, blank=True, null=True)

    summon_tier_one = models.CharField(
        max_length=2, choices=Scaling.choices, default=None, blank=True, null=True)
    summon_tier_two = models.CharField(
        max_length=2, choices=Scaling.choices, default=None, blank=True, null=True)
    summon_tier_three = models.CharField(
        max_length=2, choices=Scaling.choices, default=None, blank=True, null=True)
    summon_tier_four = models.CharField(
        max_length=2, choices=Scaling.choices, default=None, blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.weapon.name} Damage"


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


class Bonuses(models.Model):
    class Meta:
        abstract = True

    max_hp = models.IntegerField(default=0)
    max_fp = models.IntegerField(default=0)
    max_ap = models.IntegerField(default=0)

    attunement_slots = models.IntegerField(default=0)
    free_movement = models.IntegerField(default=0)

    vitality = models.IntegerField(default=0)
    endurance = models.IntegerField(default=0)
    strength = models.IntegerField(default=0)
    dexterity = models.IntegerField(default=0)
    attunement = models.IntegerField(default=0)
    intelligence = models.IntegerField(default=0)
    faith = models.IntegerField(default=0)

    athletics = models.IntegerField(default=0)
    acrobatics = models.IntegerField(default=0)
    perception = models.IntegerField(default=0)
    firekeeping = models.IntegerField(default=0)
    sanity = models.IntegerField(default=0)
    stealth = models.IntegerField(default=0)
    precision = models.IntegerField(default=0)
    diplomacy = models.IntegerField(default=0)

    knowledge_magics = models.IntegerField(default=0)
    knowledge_history = models.IntegerField(default=0)
    knowledge_monsters = models.IntegerField(default=0)
    knowledge_cosmic = models.IntegerField(default=0)

    resist_physical = models.IntegerField(default=0)
    resist_magic = models.IntegerField(default=0)
    resist_fire = models.IntegerField(default=0)
    resist_lightning = models.IntegerField(default=0)
    resist_dark = models.IntegerField(default=0)
    flat_physical = models.IntegerField(default=0)
    flat_magic = models.IntegerField(default=0)
    flat_fire = models.IntegerField(default=0)
    flat_lightning = models.IntegerField(default=0)
    flat_dark = models.IntegerField(default=0)

    curse = models.IntegerField(default=0)
    frost = models.IntegerField(default=0)
    bleed = models.IntegerField(default=0)
    poison = models.IntegerField(default=0)
    toxic = models.IntegerField(default=0)
    poise = models.IntegerField(default=0)


class WeaponProfBonuses(Bonuses):
    weapon_prof = models.OneToOneField(
        WeaponProfFeat, on_delete=models.CASCADE, primary_key=True, related_name="bonuses")

    def __str__(self) -> str:
        return f"{self.weapon_prof.name} Bonuses"


class DestinyFeatBonuses(Bonuses):
    destiny_feat = models.OneToOneField(
        DestinyFeat, on_delete=models.CASCADE, primary_key=True, related_name="bonuses")

    def __str__(self) -> str:
        return f"{self.destiny_feat.name} Bonuses"


class RingBonuses(Bonuses):
    ring = models.OneToOneField(
        Ring, on_delete=models.CASCADE, primary_key=True, related_name="bonuses")

    def __str__(self) -> str:
        return f"{self.ring.name} Bonuses"


class ArtifactBonuses(Bonuses):
    artifact = models.OneToOneField(
        Artifact, on_delete=models.CASCADE, primary_key=True, related_name="bonuses")

    def __str__(self) -> str:
        return f"{self.artifact.name} Bonuses"


class ArmorBonuses(Bonuses):
    armor = models.OneToOneField(
        Armor, on_delete=models.CASCADE, primary_key=True, related_name="bonuses")

    def __str__(self) -> str:
        return f"{self.armor.name} Bonuses"


class WeaponBonuses(Bonuses):
    weapon = models.OneToOneField(
        Weapon, on_delete=models.CASCADE, primary_key=True, related_name="bonuses")

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
    
class Spell(models.Model):
    created_at = models.DateTimeField("date created")
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=200)

    req_int = models.IntegerField(default=0)
    req_fai = models.IntegerField(default=0)

    cost_attunement = models.IntegerField(default=1)
    cost_ap = models.IntegerField(default=0)
    cost_fp = models.IntegerField(default=0)

    is_slow = models.BooleanField(default=False)
    category = models.CharField(max_length=200)

    base_dmg = models.CharField(max_length=200)
    range = models.CharField(max_length=200)
    duration = models.CharField(max_length=200)

    charged_spell = models.CharField(max_length=200)

    def __str__(self) -> str:
        return self.name


    class StatusType(models.TextChoices):
        FROST = "FROST", _("Frost")
        BLEED = "BLEED", _("Bleed")
        POISON = "POISON", _("Poison")
        TOXIC = "TOXIC", _("Toxic")


"""
