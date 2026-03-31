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


class SizeCategories(models.TextChoices):
    TINY = "TINY", _("Tiny")
    SMALL = "SMALL", _("Small")
    MEDIUM = "MEDIUM", _("Medium")
    LARGE = "LARGE", _("Large")
    MASSIVE = "MASSIVE", _("Massive")
    GARGANTUAN = "GARGANTUAN", _("Gargantuan")
    ASTRONOMICAL = "ASTRONOMICAL", _("Astronomical")


class WeaponForm(models.TextChoices):
    """For trick weapons - identifies which form a related entry belongs to."""
    PRIMARY = "primary", _("Primary Form")
    SECONDARY = "secondary", _("Secondary Form")


class ElementTypeExpanded(models.TextChoices):
    # Damage Types (8)
    PHYSICAL = "PHYSICAL", _("Physical")
    MAGIC = "MAGIC", _("Magic")
    FIRE = "FIRE", _("Fire")
    LIGHTNING = "LIGHTNING", _("Lightning")
    DARK = "DARK", _("Dark")
    TRUE = "TRUE", _("True Damage")
    DAMAGE_FP = "DAMAGE_FP", _("FP Damage")  # Renamed from UNFOCUS
    DAMAGE_AP = "DAMAGE_AP", _("AP Damage")  # New

    # Status Buildup (6)
    BLEED = "BLEED", _("Bleed")
    POISON = "POISON", _("Poison")
    TOXIC = "TOXIC", _("Toxic")
    FROST = "FROST", _("Frostbite")
    CURSE = "CURSE", _("Curse")
    POISE = "POISE", _("Poise")

    # Restoration (3)
    HEAL = "HEAL", _("HP Healing")
    RESTORE_FP = "RESTORE_FP", _("FP Restoration")  # Renamed from FOCUS
    RESTORE_AP = "RESTORE_AP", _("AP Restoration")  # New

    # Manual/User-Defined (1)
    VARYING = "VARYING", _("Varying")  # Foundry ignores - users define manually

    # Equipment (1)
    DURABILITY = "DURABILITY", _("Durability")

    # REMOVED: REDUCE (replaced by CF4 Protection System)


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
    MUSICAL_INSTRUMENTS = "MUSICAL_INSTRUMENTS", _("Musical Instruments")


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
        max_length=20,
        choices=WeaponProfTree.choices
    )
    level = models.IntegerField(default=3)
    usage_formula = models.ForeignKey(
        UsageFormula, models.SET_NULL, blank=True, null=True, default=None)
    description = models.TextField(max_length=4096)
    is_official = models.BooleanField(default=True)

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
    is_official = models.BooleanField(default=True)

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
    is_official = models.BooleanField(default=True)
    campaign = models.ForeignKey(
        'campaigns.Campaign', on_delete=models.CASCADE, blank=True, null=True,
        help_text="If set, this weapon skill belongs to a specific campaign (custom)")
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    created_by = models.ForeignKey(
        'auth.User', on_delete=models.DO_NOTHING, blank=True, null=True,
        related_name='created_weapon_skills')
    updated_at = models.DateTimeField(auto_now=True, null=True)
    updated_by = models.ForeignKey(
        'auth.User', on_delete=models.DO_NOTHING, blank=True, null=True,
        related_name='updated_weapon_skills')

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
    campaign = models.ForeignKey(
        'campaigns.Campaign', models.CASCADE, blank=True, null=True, related_name="custom_spells")
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

class Spirit(models.Model):
    class SpiritTier(models.TextChoices):
        ONE = "ONE", _("Tier One")
        TWO = "TWO", _("Tier Two")
        THREE = "THREE", _("Tier Three")
        FOUR = "FOUR", _("Tier Four")
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, models.DO_NOTHING, blank=True, null=True, related_name="spirit_created_by")
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User, models.DO_NOTHING, blank=True, null=True, related_name="spirit_updated_by")
    is_official = models.BooleanField(default=False)
    campaign = models.ForeignKey(
        'campaigns.Campaign', models.CASCADE, blank=True, null=True, related_name="custom_spirits")
    tier = models.CharField(max_length=5, choices=SpiritTier.choices, default=SpiritTier.ONE)
    creature = models.CharField(max_length=200, blank=True, default="")
    size = models.CharField(max_length=12, choices=SizeCategories.choices, default=SizeCategories.MEDIUM)
    range = models.CharField(max_length=200, blank=True, default="")
    condition = models.CharField(max_length=200, blank=True, default="")
    description = models.TextField(max_length=1024)
    att_cost = models.IntegerField(default=1, help_text="Attunement slot cost")
    fp = models.IntegerField(default=0, help_text="FP cost")
    ap = models.IntegerField(default=0, help_text="AP cost")

    def __str__(self) -> str:
        return f"{self.name} (Tier {self.get_tier_display()})"

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
    campaign = models.ForeignKey(
        'campaigns.Campaign', models.CASCADE, blank=True, null=True, related_name="custom_items")
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
    is_official = models.BooleanField(default=True)
    campaign = models.ForeignKey(
        'campaigns.Campaign', models.CASCADE, blank=True, null=True, related_name="custom_rings")

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
    is_official = models.BooleanField(default=True)
    campaign = models.ForeignKey(
        'campaigns.Campaign', models.CASCADE, blank=True, null=True, related_name="custom_artifacts")

    def __str__(self) -> str:
        return self.name


class ArtifactUpgrade(models.Model):
    """
    Upgrade path for an artifact.
    Each upgrade can influence spells, skills, weapon prof feats, destiny feats.
    GM controls visibility to players via two toggles.
    """

    artifact = models.ForeignKey(
        Artifact,
        on_delete=models.CASCADE,
        related_name="upgrades",
        help_text="The artifact this upgrade belongs to"
    )

    name = models.CharField(
        max_length=200,
        help_text="Name of this upgrade (e.g., 'Flame Infusion', 'Dark Path')"
    )

    unlock_requirements = models.TextField(
        max_length=2048,
        blank=True,
        help_text="Text describing what player must do to unlock (e.g., 'Defeat 10 enemies with fire magic')"
    )

    visible = models.BooleanField(
        default=False,
        help_text="If true, player can see this upgrade exists. If false, completely hidden from player."
    )

    requirements_visible = models.BooleanField(
        default=False,
        help_text="If true, player can see the unlock requirements. If false, requirements are hidden even if upgrade is visible."
    )

    description = models.TextField(
        max_length=4096,
        help_text="What this upgrade does (visible to player if visible=true)"
    )

    influenced_spells = models.ManyToManyField(
        'Spell',
        blank=True,
        related_name="artifact_upgrade_influences",
        help_text="Spells this upgrade affects"
    )

    influenced_weapon_prof_feats = models.ManyToManyField(
        WeaponProfFeat,
        blank=True,
        related_name="artifact_upgrade_influences",
        help_text="Weapon proficiency feats this upgrade affects"
    )

    influenced_destiny_feats = models.ManyToManyField(
        DestinyFeat,
        blank=True,
        related_name="artifact_upgrade_influences",
        help_text="Destiny feats this upgrade affects"
    )

    influenced_weapon_skills = models.ManyToManyField(
        WeaponSkill,
        blank=True,
        related_name="artifact_upgrade_influences",
        help_text="Weapon skills this upgrade affects"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        visibility_status = 'Visible' if self.visible else 'Hidden'
        requirements_status = 'Req:Visible' if self.requirements_visible else 'Req:Hidden'
        return f"{self.artifact.name}: {self.name} ({visibility_status}, {requirements_status})"

    class Meta:
        ordering = ['artifact__name', 'name']
        unique_together = ['artifact', 'name']


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
    campaign = models.ForeignKey(
        'campaigns.Campaign', models.CASCADE, blank=True, null=True, related_name="custom_armors")
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
        WIND_INSTRUMENT = "WIND_INSTRUMENT", _("Wind Instrument")
        STRING_INSTRUMENT = "STRING_INSTRUMENT", _("String Instrument")
        PERCUSSION_INSTRUMENT = "PERCUSSION_INSTRUMENT", _("Percussion Instrument")
        TONGUE_INSTRUMENT = "TONGUE_INSTRUMENT", _("Tongue Instrument")
        HORN_INSTRUMENT = "HORN_INSTRUMENT", _("Horn Instrument")

    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, models.DO_NOTHING, blank=True, null=True, related_name="weapon_created_by")
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User, models.DO_NOTHING, blank=True, null=True, related_name="weapon_updated_by")
    is_official = models.BooleanField(default=False)
    campaign = models.ForeignKey(
        'campaigns.Campaign', models.CASCADE, blank=True, null=True, related_name="custom_weapons")

    is_trick = models.BooleanField(default=False)
    is_twin = models.BooleanField(default=False)
    weapon_type = models.CharField(max_length=25, choices=WeaponType.choices)
    second_type = models.CharField(
        max_length=25, choices=WeaponType.choices, blank=True, null=True, default=None)

    # Primary form stats
    ap = models.IntegerField(default=3)
    skill_primary = models.ForeignKey(
        WeaponSkill, models.SET_NULL, blank=True, null=True, default=None)
    skill_secondary = models.ForeignKey(
        WeaponSkill, models.SET_NULL, blank=True, null=True, default=None, related_name="weapon_skill_secondary")
    infusion = models.CharField(
        max_length=9, choices=ElementType.choices, blank=True, null=True, default=None)

    # CF3: Secondary form stats (for trick weapons)
    second_ap = models.IntegerField(blank=True, null=True, default=None)
    second_skill_primary = models.ForeignKey(
        WeaponSkill, models.SET_NULL, blank=True, null=True, default=None, related_name="weapon_second_skill_primary")
    second_skill_secondary = models.ForeignKey(
        WeaponSkill, models.SET_NULL, blank=True, null=True, default=None, related_name="weapon_second_skill_secondary")
    second_infusion = models.CharField(
        max_length=9, choices=ElementType.choices, blank=True, null=True, default=None)

    usage_formula = models.ForeignKey(
        UsageFormula, models.SET_NULL, blank=True, null=True, default=None)

    description = models.TextField(max_length=512)
    durability = models.IntegerField(default=10)

    def __str__(self) -> str:
        return self.name


class SpellScaling(models.Model):
    """Spell scaling for catalyst weapons (staffs, talismans, etc.)."""
    class SpellStat(models.TextChoices):
        STRENGTH = "STR", _("Strength")
        DEXTERITY = "DEX", _("Dexterity")
        INTELLIGENCE = "INT", _("Intelligence")
        FAITH = "FAI", _("Faith")
    stat = models.CharField(max_length=3, choices=SpellStat.choices)
    requirement = models.IntegerField(default=0)
    value = models.CharField(max_length=2, choices=ScalingValue.choices)
    weapon = models.ForeignKey(
        Weapon, on_delete=models.CASCADE, related_name="spell_scaling")
    # CF3: Trick Weapon System - form field for per-form spell scaling
    form = models.CharField(
        max_length=9, choices=WeaponForm.choices, default=WeaponForm.PRIMARY)

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
        # Spirit tiers removed - see SpiritScaling for spirit tier scaling
    type = models.CharField(max_length=9, choices=ScalingType.choices)
    stat = models.CharField(max_length=3, choices=ScalingStat.choices)
    weapon = models.ForeignKey(
        Weapon, on_delete=models.CASCADE, related_name="scaling")
    # CF3: Trick Weapon System - form field for per-form scaling
    form = models.CharField(
        max_length=9, choices=WeaponForm.choices, default=WeaponForm.PRIMARY)


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
    # CF3: Trick Weapon System - form field for per-form dice
    form = models.CharField(
        max_length=9, choices=WeaponForm.choices, default=WeaponForm.PRIMARY)


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

class SpiritDice(Dice):
    spirit = models.ForeignKey(
        Spirit, on_delete=models.CASCADE, related_name="dice")

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
    # CF3: Changed from OneToOneField to ForeignKey to support per-form requirements
    weapon = models.ForeignKey(
        Weapon, on_delete=models.CASCADE, related_name="requirements")
    # CF3: Trick Weapon System - form field for per-form requirements
    form = models.CharField(
        max_length=9, choices=WeaponForm.choices, default=WeaponForm.PRIMARY)

    class Meta:
        # Ensure only one requirement entry per weapon + form combination
        unique_together = ['weapon', 'form']

    def __str__(self) -> str:
        return f"{self.weapon.name} Requirements ({self.form})"
    
class SpellRequirements(models.Model):
    str = models.IntegerField(default=0)
    dex = models.IntegerField(default=0)
    int = models.IntegerField(default=0)
    fai = models.IntegerField(default=0)
    spell = models.OneToOneField(
        Spell, on_delete=models.CASCADE, primary_key=True, related_name="requirements")

    def __str__(self) -> str:
        return f"{self.spell.name} Requirements"

class SpiritRequirements(models.Model):
    str = models.IntegerField(default=0)
    dex = models.IntegerField(default=0)
    int = models.IntegerField(default=0)
    fai = models.IntegerField(default=0)
    spirit = models.OneToOneField(
        Spirit, on_delete=models.CASCADE, primary_key=True, related_name="requirements")

    def __str__(self) -> str:
        return f"{self.spirit.name} Requirements"

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
        return f"{self.item.name} Bonuses"

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


# Character creation models for lineages, bloodlines, and backgrounds
class Background(models.Model):
    """Starting character backgrounds with HP and base stats"""

    # Identity
    name = models.CharField(max_length=60, unique=True)
    description = models.TextField(max_length=2048, blank=True)

    # Starting resources
    starting_hp = models.IntegerField()
    starting_fate_points = models.IntegerField(default=2)

    # Base stats (all default to 10)
    vitality = models.IntegerField(default=10)
    endurance = models.IntegerField(default=10)
    strength = models.IntegerField(default=10)
    dexterity = models.IntegerField(default=10)
    attunement = models.IntegerField(default=10)
    intelligence = models.IntegerField(default=10)
    faith = models.IntegerField(default=10)

    # Special rules for Chaotic Tarnished
    has_special_rules = models.BooleanField(default=False)
    special_rules = models.TextField(max_length=1024, blank=True)

    # Metadata
    is_official = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.name} (HP: {self.starting_hp})"

    class Meta:
        ordering = ['name']


class Lineage(models.Model):
    """Base lineage types with abilities stored as JSON"""

    # Identity
    name = models.CharField(max_length=60, unique=True)
    subtitle = models.CharField(
        max_length=100,
        help_text="Short descriptor (e.g., 'Wayfarers of Death', 'Masters of the Hollowed Earth')"
    )
    description = models.TextField(
        max_length=4096,
        help_text="Full lineage lore and background description"
    )

    # Physical characteristics
    appearance = models.TextField(
        max_length=1024,
        help_text="Physical appearance and distinguishing features"
    )
    language = models.CharField(
        max_length=60,
        help_text="Primary language spoken by this lineage"
    )
    lifespan_min = models.IntegerField(
        help_text="Minimum lifespan in years"
    )
    lifespan_max = models.IntegerField(
        help_text="Maximum lifespan in years"
    )

    # Abilities stored as structured JSON for flexibility
    # Contains vision, skill_bonuses, resistances, special_abilities, etc.
    base_abilities = models.JSONField(
        help_text='Stores lineage abilities as JSON. Example for Ferno lineage: '
                  '{"vision": {"type": "darkvision", "range": 60}, '
                  '"skill_bonuses": {"Sanity": 2}, '
                  '"special_abilities": [{"name": "Auto-detect Undying", "description": "Automatically detect undying stacks on visible creatures", "type": "passive"}], '
                  '"regeneration": {"hp": {"base": "1d2/hour", "condition": "in full darkness", "scaling": [{"level": 17, "value": "1d4/hour"}]}}}'
    )

    # Metadata
    is_official = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.name} ({self.subtitle})"

    class Meta:
        ordering = ['name']


class Bloodline(models.Model):
    """Bloodline variants that modify base lineage abilities"""

    lineage = models.ForeignKey(
        Lineage,
        on_delete=models.CASCADE,
        related_name='bloodlines',
        help_text="The parent lineage this bloodline belongs to"
    )
    name = models.CharField(
        max_length=60,
        help_text="Bloodline name (e.g., 'Death Touched Ferno', 'Geode Grme')"
    )
    description = models.TextField(
        max_length=2048,
        help_text="Full bloodline description and what makes it unique"
    )

    # Lists which base abilities this bloodline replaces
    replaces_abilities = models.JSONField(
        default=list,
        blank=True,
        help_text='List of base lineage ability keys that this bloodline removes. '
                  'The bloodline provides replacement abilities via new_abilities. '
                  'Example for Death Touched Ferno: ["regeneration"]'
    )

    # New abilities this bloodline provides (same structure as lineage base_abilities)
    new_abilities = models.JSONField(
        default=dict,
        blank=True,
        help_text='Abilities this bloodline grants (replaces removed abilities). Uses same structure as base_abilities. '
                  'Example for Death Touched Ferno: '
                  '{"special_abilities": [{"name": "Ghostflame Respawn", "description": "Can respawn in place on successful undying check via white ghostflame", "type": "passive"}], '
                  '"regeneration": {"hp": {"base": "-1d2/hour", "condition": "in bright light"}}}'
    )

    # Some bloodlines require special unlocks
    has_unlock_requirement = models.BooleanField(
        default=False,
        help_text="Check if this bloodline requires special conditions to unlock"
    )
    unlock_requirement = models.TextField(
        max_length=512,
        blank=True,
        help_text='What the player must do to unlock this bloodline. Leave blank for bloodlines available at character creation. '
                  'Example for Ancient Scale Dragonkind: "Regular Dragonkind level 10+ with communion of 3+ ancient dragon types"'
    )

    # Metadata
    is_official = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.lineage.name}: {self.name}"

    class Meta:
        ordering = ['lineage__name', 'name']
        unique_together = ['lineage', 'name']


# =============================================================================
# Protection System Models (CF4)
# =============================================================================

class ProtectionDamageType(models.TextChoices):
    """Damage types that can be protected against. TRUE is excluded (bypasses all protection)."""
    PHYSICAL = "PHYSICAL", _("Physical")
    MAGIC = "MAGIC", _("Magic")
    FIRE = "FIRE", _("Fire")
    LIGHTNING = "LIGHTNING", _("Lightning")
    DARK = "DARK", _("Dark")


class ProtectionBuildupType(models.TextChoices):
    """Status buildup types that can be protected against."""
    BLEED = "BLEED", _("Bleed")
    POISON = "POISON", _("Poison")
    TOXIC = "TOXIC", _("Toxic")
    FROST = "FROST", _("Frost")
    CURSE = "CURSE", _("Curse")
    POISE = "POISE", _("Poise")


class ProtectionConditionType(models.TextChoices):
    """All conditions that can be protected against (includes effect-triggered)."""
    # Direct conditions
    GRAPPLED = "GRAPPLED", _("Grappled")
    RESTRAINED = "RESTRAINED", _("Restrained")
    PRONE = "PRONE", _("Prone")
    MOUNTING = "MOUNTING", _("Mounting")
    IMPAIRED_VISION = "IMPAIRED_VISION", _("Impaired Vision")
    DEAFENED = "DEAFENED", _("Deafened")
    DAZED = "DAZED", _("Dazed")
    LIMB_FRACTURE = "LIMB_FRACTURE", _("Limb Fracture")
    LOCKED_UP = "LOCKED_UP", _("Locked Up")
    FRENZY = "FRENZY", _("Frenzy")
    BERSERK = "BERSERK", _("Berserk")
    EXHAUSTION = "EXHAUSTION", _("Exhaustion")
    # Effect-triggered conditions (from buildup)
    STAGGERED = "STAGGERED", _("Staggered")
    BLED_OUT = "BLED_OUT", _("Bled Out")
    POISONED = "POISONED", _("Poisoned")
    BADLY_POISONED = "BADLY_POISONED", _("Badly Poisoned")
    FROSTBITTEN = "FROSTBITTEN", _("Frostbitten")
    CURSED = "CURSED", _("Cursed")


class PercentageTiming(models.TextChoices):
    """When percentage reduction is applied in the damage pipeline."""
    INITIAL = "INITIAL", _("Before Reductions")
    FINAL = "FINAL", _("After Reductions")


class StackingBehavior(models.TextChoices):
    """How protection from the same source stacks."""
    APPEND = "APPEND", _("Append")
    OVERWRITE = "OVERWRITE", _("Overwrite")


class SpellDamageProtection(models.Model):
    """Damage protection granted by a spell."""
    spell = models.ForeignKey(Spell, on_delete=models.CASCADE, related_name="damage_protection")
    type = models.CharField(max_length=10, choices=ProtectionDamageType.choices)
    tiers = models.IntegerField(default=0)
    flat = models.IntegerField(default=0)
    dice_count = models.IntegerField(default=0)  # e.g., 1 for 1d6
    dice_value = models.IntegerField(default=0)  # e.g., 6 for 1d6
    percentage = models.IntegerField(default=0)  # 0-100
    percentage_timing = models.CharField(max_length=7, choices=PercentageTiming.choices, default=PercentageTiming.FINAL)
    duration_turns = models.IntegerField(default=0)
    duration_attacks = models.IntegerField(default=0)
    apply_to_caster = models.BooleanField(default=False)
    apply_to_target = models.BooleanField(default=True)
    stacking = models.CharField(max_length=9, choices=StackingBehavior.choices, default=StackingBehavior.OVERWRITE)
    scaling_source = models.JSONField(default=dict, blank=True)

    def __str__(self) -> str:
        return f"{self.spell.name} - {self.type} Protection"


class SpellBuildupProtection(models.Model):
    """Status buildup protection granted by a spell."""
    spell = models.ForeignKey(Spell, on_delete=models.CASCADE, related_name="buildup_protection")
    type = models.CharField(max_length=10, choices=ProtectionBuildupType.choices)
    flat = models.IntegerField(default=0)  # NO tiers for buildup
    dice_count = models.IntegerField(default=0)
    dice_value = models.IntegerField(default=0)
    percentage = models.IntegerField(default=0)
    percentage_timing = models.CharField(max_length=7, choices=PercentageTiming.choices, default=PercentageTiming.FINAL)
    duration_turns = models.IntegerField(default=0)
    duration_attacks = models.IntegerField(default=0)
    apply_to_caster = models.BooleanField(default=False)
    apply_to_target = models.BooleanField(default=True)
    stacking = models.CharField(max_length=9, choices=StackingBehavior.choices, default=StackingBehavior.OVERWRITE)
    scaling_source = models.JSONField(default=dict, blank=True)

    def __str__(self) -> str:
        return f"{self.spell.name} - {self.type} Buildup Protection"


class SpellConditionProtection(models.Model):
    """Condition immunity granted by a spell."""
    spell = models.ForeignKey(Spell, on_delete=models.CASCADE, related_name="condition_protection")
    condition = models.CharField(max_length=20, choices=ProtectionConditionType.choices)
    duration_turns = models.IntegerField(default=0)
    apply_to_caster = models.BooleanField(default=False)
    apply_to_target = models.BooleanField(default=True)
    # NO stacking - immunity is binary

    def __str__(self) -> str:
        return f"{self.spell.name} - {self.condition} Immunity"


class SpiritDamageProtection(models.Model):
    """Damage protection granted by a spirit."""
    spirit = models.ForeignKey(Spirit, on_delete=models.CASCADE, related_name="damage_protection")
    type = models.CharField(max_length=10, choices=ProtectionDamageType.choices)
    tiers = models.IntegerField(default=0)
    flat = models.IntegerField(default=0)
    dice_count = models.IntegerField(default=0)
    dice_value = models.IntegerField(default=0)
    percentage = models.IntegerField(default=0)
    percentage_timing = models.CharField(max_length=7, choices=PercentageTiming.choices, default=PercentageTiming.FINAL)
    duration_turns = models.IntegerField(default=0)
    duration_attacks = models.IntegerField(default=0)
    apply_to_caster = models.BooleanField(default=False)
    apply_to_target = models.BooleanField(default=True)
    stacking = models.CharField(max_length=9, choices=StackingBehavior.choices, default=StackingBehavior.OVERWRITE)
    scaling_source = models.JSONField(default=dict, blank=True)

    def __str__(self) -> str:
        return f"{self.spirit.name} - {self.type} Protection"


class SpiritBuildupProtection(models.Model):
    """Status buildup protection granted by a spirit."""
    spirit = models.ForeignKey(Spirit, on_delete=models.CASCADE, related_name="buildup_protection")
    type = models.CharField(max_length=10, choices=ProtectionBuildupType.choices)
    flat = models.IntegerField(default=0)
    dice_count = models.IntegerField(default=0)
    dice_value = models.IntegerField(default=0)
    percentage = models.IntegerField(default=0)
    percentage_timing = models.CharField(max_length=7, choices=PercentageTiming.choices, default=PercentageTiming.FINAL)
    duration_turns = models.IntegerField(default=0)
    duration_attacks = models.IntegerField(default=0)
    apply_to_caster = models.BooleanField(default=False)
    apply_to_target = models.BooleanField(default=True)
    stacking = models.CharField(max_length=9, choices=StackingBehavior.choices, default=StackingBehavior.OVERWRITE)
    scaling_source = models.JSONField(default=dict, blank=True)

    def __str__(self) -> str:
        return f"{self.spirit.name} - {self.type} Buildup Protection"


class SpiritConditionProtection(models.Model):
    """Condition immunity granted by a spirit."""
    spirit = models.ForeignKey(Spirit, on_delete=models.CASCADE, related_name="condition_protection")
    condition = models.CharField(max_length=20, choices=ProtectionConditionType.choices)
    duration_turns = models.IntegerField(default=0)
    apply_to_caster = models.BooleanField(default=False)
    apply_to_target = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.spirit.name} - {self.condition} Immunity"


# =============================================================================
# Restoration System Models (Reduce Buildup, Cure Condition, Cure Effect)
# =============================================================================

class CurableConditionType(models.TextChoices):
    """Conditions that can be cured via cure-condition.
    Excludes effect-triggered conditions (BledOut, Poisoned, etc.) which require cure-effect."""
    GRAPPLED = "GRAPPLED", _("Grappled")
    RESTRAINED = "RESTRAINED", _("Restrained")
    PRONE = "PRONE", _("Prone")
    MOUNTING = "MOUNTING", _("Mounting")
    IMPAIRED_VISION = "IMPAIRED_VISION", _("Impaired Vision")
    DEAFENED = "DEAFENED", _("Deafened")
    DAZED = "DAZED", _("Dazed")
    LIMB_FRACTURE = "LIMB_FRACTURE", _("Limb Fracture")
    LOCKED_UP = "LOCKED_UP", _("Locked Up")
    FRENZY = "FRENZY", _("Frenzy")
    BERSERK = "BERSERK", _("Berserk")
    EXHAUSTION = "EXHAUSTION", _("Exhaustion")


class StatusEffectType(models.TextChoices):
    """Status effects that can be cured via cure-effect.
    These are buildup-triggered effects - curing also resets the buildup."""
    BLEED = "BLEED", _("Bleed (cures Bled Out)")
    POISON = "POISON", _("Poison (cures Poisoned)")
    TOXIC = "TOXIC", _("Toxic (cures Badly Poisoned)")
    FROST = "FROST", _("Frost (cures Frostbitten)")
    CURSE = "CURSE", _("Curse (cures Cursed)")
    POISE = "POISE", _("Poise (cures Staggered)")


class SpellReduceBuildup(models.Model):
    """Buildup reduction granted by a spell."""
    spell = models.ForeignKey(Spell, on_delete=models.CASCADE, related_name="reduce_buildup")
    buildup_type = models.CharField(max_length=10, choices=ProtectionBuildupType.choices)
    dice_count = models.IntegerField(default=0, help_text="Number of dice (e.g., 1 for 1d4)")
    dice_value = models.IntegerField(default=0, help_text="Dice sides (e.g., 4 for 1d4)")
    flat_bonus = models.IntegerField(default=0, help_text="Flat amount added to roll")
    scaling_source = models.JSONField(default=dict, blank=True, help_text="Optional scaling source")

    def __str__(self) -> str:
        dice_str = f"{self.dice_count}d{self.dice_value}" if self.dice_count > 0 else ""
        flat_str = f"+{self.flat_bonus}" if self.flat_bonus > 0 else ""
        return f"{self.spell.name} - Reduce {self.buildup_type} {dice_str}{flat_str}"


class SpiritReduceBuildup(models.Model):
    """Buildup reduction granted by a spirit."""
    spirit = models.ForeignKey(Spirit, on_delete=models.CASCADE, related_name="reduce_buildup")
    buildup_type = models.CharField(max_length=10, choices=ProtectionBuildupType.choices)
    dice_count = models.IntegerField(default=0, help_text="Number of dice (e.g., 1 for 1d4)")
    dice_value = models.IntegerField(default=0, help_text="Dice sides (e.g., 4 for 1d4)")
    flat_bonus = models.IntegerField(default=0, help_text="Flat amount added to roll")
    scaling_source = models.JSONField(default=dict, blank=True, help_text="Optional scaling source")

    def __str__(self) -> str:
        dice_str = f"{self.dice_count}d{self.dice_value}" if self.dice_count > 0 else ""
        flat_str = f"+{self.flat_bonus}" if self.flat_bonus > 0 else ""
        return f"{self.spirit.name} - Reduce {self.buildup_type} {dice_str}{flat_str}"


class SpellCureCondition(models.Model):
    """Condition curing granted by a spell. One entry per condition cured."""
    spell = models.ForeignKey(Spell, on_delete=models.CASCADE, related_name="cure_conditions")
    condition = models.CharField(max_length=20, choices=CurableConditionType.choices)

    class Meta:
        unique_together = ['spell', 'condition']

    def __str__(self) -> str:
        return f"{self.spell.name} - Cures {self.condition}"


class SpiritCureCondition(models.Model):
    """Condition curing granted by a spirit. One entry per condition cured."""
    spirit = models.ForeignKey(Spirit, on_delete=models.CASCADE, related_name="cure_conditions")
    condition = models.CharField(max_length=20, choices=CurableConditionType.choices)

    class Meta:
        unique_together = ['spirit', 'condition']

    def __str__(self) -> str:
        return f"{self.spirit.name} - Cures {self.condition}"


class SpellCureEffect(models.Model):
    """Status effect curing granted by a spell. Cures the triggered condition AND resets buildup."""
    spell = models.ForeignKey(Spell, on_delete=models.CASCADE, related_name="cure_effects")
    effect_type = models.CharField(max_length=10, choices=StatusEffectType.choices)

    class Meta:
        unique_together = ['spell', 'effect_type']

    def __str__(self) -> str:
        return f"{self.spell.name} - Cures {self.effect_type} effect"


class SpiritCureEffect(models.Model):
    """Status effect curing granted by a spirit. Cures the triggered condition AND resets buildup."""
    spirit = models.ForeignKey(Spirit, on_delete=models.CASCADE, related_name="cure_effects")
    effect_type = models.CharField(max_length=10, choices=StatusEffectType.choices)

    class Meta:
        unique_together = ['spirit', 'effect_type']

    def __str__(self) -> str:
        return f"{self.spirit.name} - Cures {self.effect_type} effect"


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
