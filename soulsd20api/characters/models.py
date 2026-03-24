"""
Normalized Character Models for SD20 Application.

This module implements a fully normalized database schema for character storage,
replacing the previous JSON blob approach for better maintainability, efficient
updates, and clear structure for team development.

Architecture:
- Character: Core identity and metadata
- One-to-One tables: Stats, Skills, Knowledge, Resources, Resistances, Statuses, etc.
- One-to-Many tables: Equipment, Proficiencies, Spells, Spirits, Skills, Feats, Companions
- Template + Overlay: Equipment stores compendium reference + modifications (not copies)
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


# =============================================================================
# CORE CHARACTER MODEL
# =============================================================================

class Character(models.Model):
    """
    Core character model containing identity and metadata.
    Related data is stored in separate normalized tables.
    """

    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    # Primary key - UUID to match existing localStorage UUIDs
    # editable=True allows clients to specify their own UUID during creation
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=True
    )

    # Owner relationship
    owner = models.ForeignKey(
        'accounts.UserProfile',
        on_delete=models.CASCADE,
        related_name='characters'
    )

    # Campaign relationship (optional - null means "in limbo" or not assigned)
    campaign = models.ForeignKey(
        'campaigns.Campaign',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='characters'
    )

    # === Identity ===
    name = models.CharField(max_length=200)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='Male')
    physical_description = models.TextField(blank=True, default='')

    # === Character Creation (locked after finalization) ===
    background_id = models.IntegerField()
    lineage_id = models.IntegerField()
    bloodline_id = models.IntegerField(null=True, blank=True)
    is_finalized = models.BooleanField(default=False)

    # === Progression ===
    level = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    souls_level = models.IntegerField(default=0)

    # === Image ===
    # Stores JSON: {"url": "https://...", "crop": {"position": {...}, "size": {...}}}
    image_url = models.TextField(blank=True, null=True)

    # === State ===
    is_active = models.BooleanField(default=True)  # Soft delete

    # === Timestamps ===
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_played = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-last_played']
        verbose_name = 'Character'
        verbose_name_plural = 'Characters'
        indexes = [
            models.Index(fields=['owner', 'is_active']),
            models.Index(fields=['name']),
            models.Index(fields=['level']),
            models.Index(fields=['background_id']),
            models.Index(fields=['lineage_id']),
        ]

    def __str__(self):
        return f"{self.name} (Lv. {self.level})"


# =============================================================================
# ONE-TO-ONE TABLES (exactly one per character)
# =============================================================================

class CharacterStats(models.Model):
    """Core character statistics (7 stats)."""
    character = models.OneToOneField(
        Character,
        on_delete=models.CASCADE,
        related_name='stats'
    )
    vitality = models.IntegerField(default=10)
    endurance = models.IntegerField(default=10)
    strength = models.IntegerField(default=10)
    dexterity = models.IntegerField(default=10)
    attunement = models.IntegerField(default=10)
    intelligence = models.IntegerField(default=10)
    faith = models.IntegerField(default=10)

    class Meta:
        verbose_name = 'Character Stats'
        verbose_name_plural = 'Character Stats'

    def __str__(self):
        return f"Stats for {self.character.name}"


class CharacterCreationStats(models.Model):
    """
    Original stats from character creation (for reset/respec).
    Especially important for Chaotic Tarnished background with rolled stats.
    """
    character = models.OneToOneField(
        Character,
        on_delete=models.CASCADE,
        related_name='creation_stats'
    )
    vitality = models.IntegerField()
    endurance = models.IntegerField()
    strength = models.IntegerField()
    dexterity = models.IntegerField()
    attunement = models.IntegerField()
    intelligence = models.IntegerField()
    faith = models.IntegerField()
    starting_hp = models.IntegerField()

    class Meta:
        verbose_name = 'Character Creation Stats'
        verbose_name_plural = 'Character Creation Stats'

    def __str__(self):
        return f"Creation Stats for {self.character.name}"


class CharacterSkills(models.Model):
    """Character skills (8 skills)."""
    character = models.OneToOneField(
        Character,
        on_delete=models.CASCADE,
        related_name='skills'
    )
    athletics = models.IntegerField(default=0)
    acrobatics = models.IntegerField(default=0)
    perception = models.IntegerField(default=0)
    fire_keeping = models.IntegerField(default=0)
    sanity = models.IntegerField(default=0)
    stealth = models.IntegerField(default=0)
    precision = models.IntegerField(default=0)
    diplomacy = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Character Skills'
        verbose_name_plural = 'Character Skills'

    def __str__(self):
        return f"Skills for {self.character.name}"


class CharacterKnowledge(models.Model):
    """Character knowledge areas (4 types)."""
    character = models.OneToOneField(
        Character,
        on_delete=models.CASCADE,
        related_name='knowledge'
    )
    magics = models.IntegerField(default=0)
    world_history = models.IntegerField(default=0)
    monsters = models.IntegerField(default=0)
    cosmic = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Character Knowledge'
        verbose_name_plural = 'Character Knowledge'

    def __str__(self):
        return f"Knowledge for {self.character.name}"


class CharacterResources(models.Model):
    """Character resources (HP, FP, AP, flasks, combat resources, fate)."""
    character = models.OneToOneField(
        Character,
        on_delete=models.CASCADE,
        related_name='resources'
    )

    # HP
    starting_hp = models.IntegerField(default=20)
    level_hp = models.IntegerField(default=0)
    current_hp = models.IntegerField(default=20)
    temp_hp = models.IntegerField(default=0)
    max_hp_bonus = models.IntegerField(default=0)
    health_die_count = models.IntegerField(default=1)
    health_die_sides = models.IntegerField(default=6)

    # FP/AP
    current_fp = models.IntegerField(default=2)
    current_ap = models.IntegerField(default=8)
    max_fp_bonus = models.IntegerField(default=0)
    max_ap_bonus = models.IntegerField(default=0)

    # Flasks
    hp_flask = models.IntegerField(default=4)
    fp_flask = models.IntegerField(default=4)
    flask_level = models.IntegerField(default=0)

    # Combat resources
    total_dodges = models.IntegerField(default=0)
    current_dodges = models.IntegerField(default=0)
    souls = models.IntegerField(default=0)
    undying = models.IntegerField(default=0)
    exhaustion = models.IntegerField(default=0)
    firekeeping_checks = models.IntegerField(default=0)
    attunement_slots = models.IntegerField(default=0)

    # Fate/Destiny
    fate_points = models.IntegerField(default=2)
    temporary_fate_points = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Character Resources'
        verbose_name_plural = 'Character Resources'

    def __str__(self):
        return f"Resources for {self.character.name}"


class CharacterResistances(models.Model):
    """Character resistances (base, flat, bonus, temp)."""
    character = models.OneToOneField(
        Character,
        on_delete=models.CASCADE,
        related_name='resistances'
    )

    # Base resistances (%)
    physical = models.IntegerField(default=0)
    magic = models.IntegerField(default=0)
    fire = models.IntegerField(default=0)
    lightning = models.IntegerField(default=0)
    dark = models.IntegerField(default=0)

    # Flat resistances
    physical_flat = models.IntegerField(default=0)
    magic_flat = models.IntegerField(default=0)
    fire_flat = models.IntegerField(default=0)
    lightning_flat = models.IntegerField(default=0)
    dark_flat = models.IntegerField(default=0)

    # Bonus resistances (from damage calculator)
    bonus_physical = models.IntegerField(default=0)
    bonus_magic = models.IntegerField(default=0)
    bonus_fire = models.IntegerField(default=0)
    bonus_lightning = models.IntegerField(default=0)
    bonus_dark = models.IntegerField(default=0)
    bonus_physical_flat = models.IntegerField(default=0)
    bonus_magic_flat = models.IntegerField(default=0)
    bonus_fire_flat = models.IntegerField(default=0)
    bonus_lightning_flat = models.IntegerField(default=0)
    bonus_dark_flat = models.IntegerField(default=0)

    # Temp bonus resistances
    temp_physical = models.IntegerField(default=0)
    temp_magic = models.IntegerField(default=0)
    temp_fire = models.IntegerField(default=0)
    temp_lightning = models.IntegerField(default=0)
    temp_dark = models.IntegerField(default=0)
    temp_physical_flat = models.IntegerField(default=0)
    temp_magic_flat = models.IntegerField(default=0)
    temp_fire_flat = models.IntegerField(default=0)
    temp_lightning_flat = models.IntegerField(default=0)
    temp_dark_flat = models.IntegerField(default=0)

    bonus_resistances_active = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Character Resistances'
        verbose_name_plural = 'Character Resistances'

    def __str__(self):
        return f"Resistances for {self.character.name}"


class CharacterStatuses(models.Model):
    """Character status effect buildup and thresholds."""
    character = models.OneToOneField(
        Character,
        on_delete=models.CASCADE,
        related_name='statuses'
    )

    # Current status buildup
    curse = models.IntegerField(default=0)
    frost = models.IntegerField(default=0)
    bleed = models.IntegerField(default=0)
    poison = models.IntegerField(default=0)
    toxic = models.IntegerField(default=0)
    poise = models.IntegerField(default=0)

    # Bonus thresholds
    bonus_curse = models.IntegerField(default=0)
    bonus_frost = models.IntegerField(default=0)
    bonus_bleed = models.IntegerField(default=0)
    bonus_poison = models.IntegerField(default=0)
    bonus_toxic = models.IntegerField(default=0)
    bonus_poise = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Character Statuses'
        verbose_name_plural = 'Character Statuses'

    def __str__(self):
        return f"Statuses for {self.character.name}"


class CharacterCombatSettings(models.Model):
    """Combat settings and calculated attribute overrides."""
    character = models.OneToOneField(
        Character,
        on_delete=models.CASCADE,
        related_name='combat_settings'
    )

    # Two-handing
    two_handing_main_hand = models.BooleanField(default=False)
    two_handing_off_hand = models.BooleanField(default=False)

    # Active companion
    active_companion_id = models.UUIDField(null=True, blank=True)

    # Calculated attribute overrides (null = use calculated value)
    dodge_cost_override = models.IntegerField(null=True, blank=True)
    dodge_distance_override = models.IntegerField(null=True, blank=True)
    item_usage_cost_override = models.IntegerField(null=True, blank=True)
    jump_horizontal_override = models.IntegerField(null=True, blank=True)
    jump_vertical_override = models.IntegerField(null=True, blank=True)
    running_jump_horizontal_override = models.IntegerField(null=True, blank=True)
    running_jump_vertical_override = models.IntegerField(null=True, blank=True)
    max_equip_load_override = models.IntegerField(null=True, blank=True)
    undying_dc_override = models.IntegerField(null=True, blank=True)
    undying_roll_mod_override = models.IntegerField(null=True, blank=True)

    # Slot toggles
    enable_5th_ring_slot = models.BooleanField(default=False)
    enable_2nd_artifact_slot = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Character Combat Settings'
        verbose_name_plural = 'Character Combat Settings'

    def __str__(self):
        return f"Combat Settings for {self.character.name}"


class CharacterProficiencyPoints(models.Model):
    """Weapon proficiency points tracking."""
    character = models.OneToOneField(
        Character,
        on_delete=models.CASCADE,
        related_name='proficiency_points'
    )
    total = models.IntegerField(default=0)
    base_from_level = models.IntegerField(default=0)
    custom_bonus = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Character Proficiency Points'
        verbose_name_plural = 'Character Proficiency Points'

    def __str__(self):
        return f"Proficiency Points for {self.character.name}"


class CharacterMiscData(models.Model):
    """
    Flexible/rarely-changed data stored as JSON.
    Used for complex nested structures that don't benefit from normalization.
    """
    character = models.OneToOneField(
        Character,
        on_delete=models.CASCADE,
        related_name='misc_data'
    )

    # User content
    notes = models.JSONField(default=dict, blank=True)  # { sections: [...] }
    field_notes = models.JSONField(default=dict, blank=True)  # { key: value }
    compendium_entries = models.JSONField(default=list, blank=True)  # User's personal compendium

    # Level-up state (temporary, complex structure)
    pending_level_up = models.JSONField(null=True, blank=True)
    has_multi_proficient = models.BooleanField(default=False)
    multi_proficient_retroactive_points = models.IntegerField(default=0)

    # Feat acquisition flags (complex nested structures)
    dual_wielding_feat_flags = models.JSONField(default=dict, blank=True)
    musical_instruments_feat_flags = models.JSONField(default=dict, blank=True)
    halberd_feat_flags = models.JSONField(default=dict, blank=True)
    protege_flags = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = 'Character Misc Data'
        verbose_name_plural = 'Character Misc Data'

    def __str__(self):
        return f"Misc Data for {self.character.name}"


# =============================================================================
# ONE-TO-MANY TABLES (variable per character)
# =============================================================================

class CharacterEquipmentSlot(models.Model):
    """
    Equipment slots - each stores reference to compendium item + modifications.

    Uses Template + Overlay pattern:
    - item_id references the compendium item (template)
    - modifications stores only the changes (overlay)
    - When displaying: Load compendium item, apply modifications
    """
    SLOT_CHOICES = [
        ('MainHand', 'Main Hand'),
        ('OffHand', 'Off Hand'),
        ('Armor', 'Armor'),
        ('Artifact', 'Artifact'),
        ('Artifact2', 'Artifact 2'),
        ('Ring1', 'Ring 1'),
        ('Ring2', 'Ring 2'),
        ('Ring3', 'Ring 3'),
        ('Ring4', 'Ring 4'),
        ('Ring5', 'Ring 5'),
    ]
    CATEGORY_CHOICES = [
        ('weapon', 'Weapon'),
        ('armor', 'Armor'),
        ('artifact', 'Artifact'),
        ('ring', 'Ring'),
    ]

    character = models.ForeignKey(
        Character,
        on_delete=models.CASCADE,
        related_name='equipment_slots'
    )
    slot_type = models.CharField(max_length=20, choices=SLOT_CHOICES)
    item_id = models.IntegerField()  # Reference to compendium item
    item_category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    item_name = models.CharField(max_length=200)  # Denormalized for display
    modifications = models.JSONField(default=dict, blank=True)  # Only overrides

    class Meta:
        verbose_name = 'Character Equipment Slot'
        verbose_name_plural = 'Character Equipment Slots'
        unique_together = ['character', 'slot_type']

    def __str__(self):
        return f"{self.character.name} - {self.slot_type}: {self.item_name}"


class CharacterWeaponProficiency(models.Model):
    """Weapon proficiency levels per tree (22 trees)."""
    TREE_CHOICES = [
        ('FIST', 'Fist'),
        ('DAGGER', 'Dagger'),
        ('STRAIGHT_THRUST', 'Straight Sword / Thrusting Sword'),
        ('KATANA_CURVED', 'Katana / Curved Sword'),
        ('ULTRA_GREAT_SWORD', 'Great Sword / Ultra Great Sword'),
        ('GREAT_AXE', 'Axe / Great Axe'),
        ('GREAT_HAMMER', 'Hammer / Great Hammer'),
        ('TWINBLADE', 'Twinblade'),
        ('SPEAR', 'Spear'),
        ('HALBERD', 'Halberd'),
        ('REAPER', 'Reaper'),
        ('WHIP', 'Whip'),
        ('CROSS_BOW', 'Bow / Crossbow'),
        ('GREAT_BOW_BALLISTA', 'Great Bow / Ballista'),
        ('GUN', 'Gun'),
        ('SHIELD', 'Shield'),
        ('SORCERY', 'Sorcery'),
        ('MIRACLE', 'Miracle'),
        ('PYROMANCY', 'Pyromancy'),
        ('HEX', 'Hex'),
        ('SPIRIT_SUMMONING', 'Spirit Summoning'),
        ('DUAL_WIELDING', 'Dual Wielding'),
    ]

    character = models.ForeignKey(
        Character,
        on_delete=models.CASCADE,
        related_name='weapon_proficiencies'
    )
    weapon_tree = models.CharField(max_length=30, choices=TREE_CHOICES)
    level = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(25)]
    )

    class Meta:
        verbose_name = 'Character Weapon Proficiency'
        verbose_name_plural = 'Character Weapon Proficiencies'
        unique_together = ['character', 'weapon_tree']

    def __str__(self):
        return f"{self.character.name} - {self.weapon_tree}: Lv.{self.level}"


class CharacterLearnedSpell(models.Model):
    """Spells the character has learned."""
    character = models.ForeignKey(
        Character,
        on_delete=models.CASCADE,
        related_name='learned_spells'
    )
    spell_id = models.IntegerField()  # Reference to compendium
    modifications = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = 'Character Learned Spell'
        verbose_name_plural = 'Character Learned Spells'
        unique_together = ['character', 'spell_id']

    def __str__(self):
        return f"{self.character.name} - Spell #{self.spell_id}"


class CharacterAttunedSpell(models.Model):
    """Spells currently attuned for use."""
    character = models.ForeignKey(
        Character,
        on_delete=models.CASCADE,
        related_name='attuned_spells'
    )
    spell_id = models.IntegerField()
    slot_number = models.IntegerField()

    class Meta:
        verbose_name = 'Character Attuned Spell'
        verbose_name_plural = 'Character Attuned Spells'
        unique_together = ['character', 'slot_number']

    def __str__(self):
        return f"{self.character.name} - Attuned Spell Slot {self.slot_number}"


class CharacterLearnedSpirit(models.Model):
    """Spirits the character has learned."""
    character = models.ForeignKey(
        Character,
        on_delete=models.CASCADE,
        related_name='learned_spirits'
    )
    spirit_id = models.IntegerField()  # Reference to compendium
    modifications = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = 'Character Learned Spirit'
        verbose_name_plural = 'Character Learned Spirits'
        unique_together = ['character', 'spirit_id']

    def __str__(self):
        return f"{self.character.name} - Spirit #{self.spirit_id}"


class CharacterAttunedSpirit(models.Model):
    """Spirits currently attuned for use."""
    character = models.ForeignKey(
        Character,
        on_delete=models.CASCADE,
        related_name='attuned_spirits'
    )
    spirit_id = models.IntegerField()
    slot_number = models.IntegerField()

    class Meta:
        verbose_name = 'Character Attuned Spirit'
        verbose_name_plural = 'Character Attuned Spirits'
        unique_together = ['character', 'slot_number']

    def __str__(self):
        return f"{self.character.name} - Attuned Spirit Slot {self.slot_number}"


class CharacterLearnedWeaponSkill(models.Model):
    """Weapon skills the character has learned."""
    character = models.ForeignKey(
        Character,
        on_delete=models.CASCADE,
        related_name='learned_weapon_skills'
    )
    skill_id = models.IntegerField()  # Reference to compendium
    modifications = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = 'Character Learned Weapon Skill'
        verbose_name_plural = 'Character Learned Weapon Skills'
        unique_together = ['character', 'skill_id']

    def __str__(self):
        return f"{self.character.name} - Weapon Skill #{self.skill_id}"


class CharacterAttunedWeaponSkill(models.Model):
    """Weapon skills currently attuned for use."""
    character = models.ForeignKey(
        Character,
        on_delete=models.CASCADE,
        related_name='attuned_weapon_skills'
    )
    skill_id = models.IntegerField()
    slot_number = models.IntegerField()

    class Meta:
        verbose_name = 'Character Attuned Weapon Skill'
        verbose_name_plural = 'Character Attuned Weapon Skills'
        unique_together = ['character', 'slot_number']

    def __str__(self):
        return f"{self.character.name} - Attuned Weapon Skill Slot {self.slot_number}"


class CharacterObtainedFeat(models.Model):
    """Obtained feats (weapon proficiency feats, destiny traits)."""
    FEAT_TYPE_CHOICES = [
        ('weapon_prof', 'Weapon Proficiency Feat'),
        ('destiny', 'Destiny Trait'),
    ]

    character = models.ForeignKey(
        Character,
        on_delete=models.CASCADE,
        related_name='obtained_feats'
    )
    feat_id = models.IntegerField()
    feat_type = models.CharField(max_length=20, choices=FEAT_TYPE_CHOICES)
    weapon_tree = models.CharField(max_length=30, blank=True)  # For weapon feats
    source = models.CharField(max_length=50, blank=True)  # How it was obtained
    source_feat_id = models.BigIntegerField(null=True, blank=True)
    is_greyed_out = models.BooleanField(default=False)
    modifications = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = 'Character Obtained Feat'
        verbose_name_plural = 'Character Obtained Feats'

    def __str__(self):
        return f"{self.character.name} - {self.feat_type} #{self.feat_id}"


class CharacterCompanion(models.Model):
    """
    Companion creatures (mini-characters).
    Fully normalized for consistency with main character structure.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=True
    )
    character = models.ForeignKey(
        Character,
        on_delete=models.CASCADE,
        related_name='companions'
    )
    name = models.CharField(max_length=200, blank=True, default='')
    companion_type = models.CharField(max_length=100, blank=True, default='')

    # Resources (nullable - not all companions have all resources)
    hp = models.IntegerField(null=True, blank=True)
    fp = models.IntegerField(null=True, blank=True)
    ap = models.IntegerField(null=True, blank=True)

    # Skills
    athletics = models.IntegerField(default=0)
    acrobatics = models.IntegerField(default=0)
    perception = models.IntegerField(default=0)
    fire_keeping = models.IntegerField(default=0)
    sanity = models.IntegerField(default=0)
    stealth = models.IntegerField(default=0)
    precision = models.IntegerField(default=0)
    diplomacy = models.IntegerField(default=0)

    # Resistances
    physical = models.IntegerField(default=0)
    magic = models.IntegerField(default=0)
    fire = models.IntegerField(default=0)
    lightning = models.IntegerField(default=0)
    dark = models.IntegerField(default=0)

    # Statuses
    frost = models.IntegerField(default=0)
    bleed = models.IntegerField(default=0)
    poison = models.IntegerField(default=0)
    toxic = models.IntegerField(default=0)
    curse = models.IntegerField(default=0)
    poise = models.IntegerField(default=0)

    # Notes
    notes = models.TextField(blank=True, default='')

    class Meta:
        verbose_name = 'Character Companion'
        verbose_name_plural = 'Character Companions'

    def __str__(self):
        return f"{self.name} (Companion of {self.character.name})"


class CharacterInventoryItem(models.Model):
    """
    Inventory items the character owns.
    Stores compendium reference + quantity. The compendium provides the full item data.
    """
    character = models.ForeignKey(
        Character,
        on_delete=models.CASCADE,
        related_name='inventory_items'
    )
    item_id = models.IntegerField()  # Reference to compendium item
    item_category = models.CharField(max_length=20)  # weapon, armor, ring, artifact, misc, tools
    item_name = models.CharField(max_length=200)  # Denormalized for display
    quantity = models.IntegerField(default=1)

    class Meta:
        verbose_name = 'Character Inventory Item'
        verbose_name_plural = 'Character Inventory Items'
        unique_together = ['character', 'item_id', 'item_category']

    def __str__(self):
        return f"{self.character.name} - {self.item_name} x{self.quantity}"


class CharacterCampaignMembership(models.Model):
    """
    Many-to-many relationship between characters and campaigns.
    A character can be assigned to multiple campaigns simultaneously.
    """
    character = models.ForeignKey(
        Character,
        on_delete=models.CASCADE,
        related_name='campaign_memberships'
    )
    campaign = models.ForeignKey(
        'campaigns.Campaign',
        on_delete=models.CASCADE,
        related_name='character_assignments'
    )
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Character Campaign Membership'
        verbose_name_plural = 'Character Campaign Memberships'
        unique_together = ['character', 'campaign']

    def __str__(self):
        return f"{self.character.name} in {self.campaign.name}"
