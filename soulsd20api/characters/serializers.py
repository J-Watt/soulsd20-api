"""
Serializers for normalized character models.

This module provides serializers for the normalized character structure,
with nested serializers for related models and proper handling of
One-to-One and One-to-Many relationships.
"""

from rest_framework import serializers
from .models import (
    Character,
    CharacterStats,
    CharacterCreationStats,
    CharacterSkills,
    CharacterKnowledge,
    CharacterResources,
    CharacterResistances,
    CharacterStatuses,
    CharacterCombatSettings,
    CharacterProficiencyPoints,
    CharacterMiscData,
    CharacterEquipmentSlot,
    CharacterWeaponProficiency,
    CharacterLearnedSpell,
    CharacterAttunedSpell,
    CharacterLearnedSpirit,
    CharacterAttunedSpirit,
    CharacterLearnedWeaponSkill,
    CharacterAttunedWeaponSkill,
    CharacterObtainedFeat,
    CharacterCompanion,
    CharacterInventoryItem,
    CharacterCampaignMembership,
)
from accounts.serializers import UserProfileMinimalSerializer


# =============================================================================
# ONE-TO-ONE SERIALIZERS
# =============================================================================

class CharacterStatsSerializer(serializers.ModelSerializer):
    """Serializer for character stats (7 stats)."""

    class Meta:
        model = CharacterStats
        exclude = ['id', 'character']


class CharacterCreationStatsSerializer(serializers.ModelSerializer):
    """Serializer for original character creation stats."""

    class Meta:
        model = CharacterCreationStats
        exclude = ['id', 'character']


class CharacterSkillsSerializer(serializers.ModelSerializer):
    """Serializer for character skills (8 skills)."""

    class Meta:
        model = CharacterSkills
        exclude = ['id', 'character']


class CharacterKnowledgeSerializer(serializers.ModelSerializer):
    """Serializer for character knowledge (4 types)."""

    class Meta:
        model = CharacterKnowledge
        exclude = ['id', 'character']


class CharacterResourcesSerializer(serializers.ModelSerializer):
    """Serializer for character resources (HP, FP, AP, etc)."""

    class Meta:
        model = CharacterResources
        exclude = ['id', 'character']


class CharacterResistancesSerializer(serializers.ModelSerializer):
    """Serializer for character resistances."""

    class Meta:
        model = CharacterResistances
        exclude = ['id', 'character']


class CharacterStatusesSerializer(serializers.ModelSerializer):
    """Serializer for character statuses."""

    class Meta:
        model = CharacterStatuses
        exclude = ['id', 'character']


class CharacterCombatSettingsSerializer(serializers.ModelSerializer):
    """Serializer for combat settings."""

    class Meta:
        model = CharacterCombatSettings
        exclude = ['id', 'character']


class CharacterProficiencyPointsSerializer(serializers.ModelSerializer):
    """Serializer for proficiency points."""

    class Meta:
        model = CharacterProficiencyPoints
        exclude = ['id', 'character']


class CharacterMiscDataSerializer(serializers.ModelSerializer):
    """Serializer for misc data (JSON fields)."""

    class Meta:
        model = CharacterMiscData
        exclude = ['id', 'character']


# =============================================================================
# ONE-TO-MANY SERIALIZERS
# =============================================================================

class CharacterEquipmentSlotSerializer(serializers.ModelSerializer):
    """Serializer for equipment slots."""

    class Meta:
        model = CharacterEquipmentSlot
        exclude = ['id', 'character']


class CharacterWeaponProficiencySerializer(serializers.ModelSerializer):
    """Serializer for weapon proficiencies."""

    class Meta:
        model = CharacterWeaponProficiency
        exclude = ['id', 'character']


class CharacterLearnedSpellSerializer(serializers.ModelSerializer):
    """Serializer for learned spells."""

    class Meta:
        model = CharacterLearnedSpell
        exclude = ['id', 'character']


class CharacterAttunedSpellSerializer(serializers.ModelSerializer):
    """Serializer for attuned spells."""

    class Meta:
        model = CharacterAttunedSpell
        exclude = ['id', 'character']


class CharacterLearnedSpiritSerializer(serializers.ModelSerializer):
    """Serializer for learned spirits."""

    class Meta:
        model = CharacterLearnedSpirit
        exclude = ['id', 'character']


class CharacterAttunedSpiritSerializer(serializers.ModelSerializer):
    """Serializer for attuned spirits."""

    class Meta:
        model = CharacterAttunedSpirit
        exclude = ['id', 'character']


class CharacterLearnedWeaponSkillSerializer(serializers.ModelSerializer):
    """Serializer for learned weapon skills."""

    class Meta:
        model = CharacterLearnedWeaponSkill
        exclude = ['id', 'character']


class CharacterAttunedWeaponSkillSerializer(serializers.ModelSerializer):
    """Serializer for attuned weapon skills."""

    class Meta:
        model = CharacterAttunedWeaponSkill
        exclude = ['id', 'character']


class CharacterObtainedFeatSerializer(serializers.ModelSerializer):
    """Serializer for obtained feats."""

    class Meta:
        model = CharacterObtainedFeat
        exclude = ['id', 'character']


class CharacterCompanionSerializer(serializers.ModelSerializer):
    """Serializer for companions (read)."""

    class Meta:
        model = CharacterCompanion
        exclude = ['character']


class CharacterCompanionWriteSerializer(serializers.ModelSerializer):
    """Serializer for writing companions - accepts client-provided UUIDs."""

    id = serializers.UUIDField(required=False)

    class Meta:
        model = CharacterCompanion
        exclude = ['character']


class CharacterInventoryItemSerializer(serializers.ModelSerializer):
    """Serializer for inventory items."""

    class Meta:
        model = CharacterInventoryItem
        exclude = ['id', 'character']


# =============================================================================
# CHARACTER SERIALIZERS
# =============================================================================

class CharacterListSerializer(serializers.ModelSerializer):
    """
    Serializer for character list view.
    Returns minimal data for listing characters.
    """

    owner = UserProfileMinimalSerializer(read_only=True)

    class Meta:
        model = Character
        fields = [
            'id',
            'name',
            'gender',
            'level',
            'background_id',
            'lineage_id',
            'bloodline_id',
            'is_finalized',
            'is_active',
            'image_url',
            'owner',
            'created_at',
            'last_played',
        ]
        read_only_fields = ['id', 'owner', 'created_at', 'last_played']


class CharacterDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for character detail view.
    Returns full character data with all nested related models.
    """

    owner = UserProfileMinimalSerializer(read_only=True)

    # One-to-One related data
    stats = CharacterStatsSerializer(read_only=True)
    creation_stats = CharacterCreationStatsSerializer(read_only=True)
    skills = CharacterSkillsSerializer(read_only=True)
    knowledge = CharacterKnowledgeSerializer(read_only=True)
    resources = CharacterResourcesSerializer(read_only=True)
    resistances = CharacterResistancesSerializer(read_only=True)
    statuses = CharacterStatusesSerializer(read_only=True)
    combat_settings = CharacterCombatSettingsSerializer(read_only=True)
    proficiency_points = CharacterProficiencyPointsSerializer(read_only=True)
    misc_data = CharacterMiscDataSerializer(read_only=True)

    # One-to-Many related data
    equipment_slots = CharacterEquipmentSlotSerializer(many=True, read_only=True)
    weapon_proficiencies = CharacterWeaponProficiencySerializer(many=True, read_only=True)
    learned_spells = CharacterLearnedSpellSerializer(many=True, read_only=True)
    attuned_spells = CharacterAttunedSpellSerializer(many=True, read_only=True)
    learned_spirits = CharacterLearnedSpiritSerializer(many=True, read_only=True)
    attuned_spirits = CharacterAttunedSpiritSerializer(many=True, read_only=True)
    learned_weapon_skills = CharacterLearnedWeaponSkillSerializer(many=True, read_only=True)
    attuned_weapon_skills = CharacterAttunedWeaponSkillSerializer(many=True, read_only=True)
    obtained_feats = CharacterObtainedFeatSerializer(many=True, read_only=True)
    companions = CharacterCompanionSerializer(many=True, read_only=True)
    inventory_items = CharacterInventoryItemSerializer(many=True, read_only=True)
    campaigns = serializers.SerializerMethodField()

    class Meta:
        model = Character
        fields = [
            'id',
            'name',
            'gender',
            'physical_description',
            'level',
            'souls_level',
            'background_id',
            'lineage_id',
            'bloodline_id',
            'is_finalized',
            'is_active',
            'image_url',
            'owner',
            'created_at',
            'updated_at',
            'last_played',
            # One-to-One
            'stats',
            'creation_stats',
            'skills',
            'knowledge',
            'resources',
            'resistances',
            'statuses',
            'combat_settings',
            'proficiency_points',
            'misc_data',
            # One-to-Many
            'equipment_slots',
            'weapon_proficiencies',
            'learned_spells',
            'attuned_spells',
            'learned_spirits',
            'attuned_spirits',
            'learned_weapon_skills',
            'attuned_weapon_skills',
            'obtained_feats',
            'companions',
            'inventory_items',
            # Campaign assignments
            'campaigns',
        ]
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at', 'last_played']

    def get_campaigns(self, obj):
        memberships = CharacterCampaignMembership.objects.filter(
            character=obj, is_active=True
        ).select_related('campaign')
        return [
            {
                'id': str(m.campaign.id),
                'name': m.campaign.name,
                'joined_at': m.joined_at.isoformat() if m.joined_at else None,
            }
            for m in memberships
        ]


class CharacterCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new character.
    Creates all required One-to-One related models automatically.
    """

    # Optional nested data for creation
    stats = CharacterStatsSerializer(required=False)
    skills = CharacterSkillsSerializer(required=False)
    knowledge = CharacterKnowledgeSerializer(required=False)
    resources = CharacterResourcesSerializer(required=False)
    resistances = CharacterResistancesSerializer(required=False)
    statuses = CharacterStatusesSerializer(required=False)
    combat_settings = CharacterCombatSettingsSerializer(required=False)
    proficiency_points = CharacterProficiencyPointsSerializer(required=False)
    misc_data = CharacterMiscDataSerializer(required=False)

    class Meta:
        model = Character
        fields = [
            'id',
            'name',
            'gender',
            'physical_description',
            'level',
            'souls_level',
            'background_id',
            'lineage_id',
            'bloodline_id',
            'is_finalized',
            'image_url',
            # Optional nested data
            'stats',
            'skills',
            'knowledge',
            'resources',
            'resistances',
            'statuses',
            'combat_settings',
            'proficiency_points',
            'misc_data',
        ]
        # Allow client-provided UUID for sync (if not provided, default uuid4 is used)
        extra_kwargs = {
            'id': {'required': False}
        }

    def create(self, validated_data):
        """Create character with all required related models."""
        # Extract nested data
        stats_data = validated_data.pop('stats', {})
        skills_data = validated_data.pop('skills', {})
        knowledge_data = validated_data.pop('knowledge', {})
        resources_data = validated_data.pop('resources', {})
        resistances_data = validated_data.pop('resistances', {})
        statuses_data = validated_data.pop('statuses', {})
        combat_settings_data = validated_data.pop('combat_settings', {})
        proficiency_points_data = validated_data.pop('proficiency_points', {})
        misc_data_data = validated_data.pop('misc_data', {})

        # Set owner from request context
        request = self.context.get('request')
        if request and hasattr(request.user, 'profile'):
            validated_data['owner'] = request.user.profile

        # Create character
        character = Character.objects.create(**validated_data)

        # Create all required One-to-One models
        CharacterStats.objects.create(character=character, **stats_data)
        CharacterSkills.objects.create(character=character, **skills_data)
        CharacterKnowledge.objects.create(character=character, **knowledge_data)
        CharacterResources.objects.create(character=character, **resources_data)
        CharacterResistances.objects.create(character=character, **resistances_data)
        CharacterStatuses.objects.create(character=character, **statuses_data)
        CharacterCombatSettings.objects.create(character=character, **combat_settings_data)
        CharacterProficiencyPoints.objects.create(character=character, **proficiency_points_data)
        CharacterMiscData.objects.create(character=character, **misc_data_data)

        return character


class CharacterUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating an existing character.
    Handles partial updates to nested One-to-One and One-to-Many models.
    """

    # One-to-One nested data for updates
    stats = CharacterStatsSerializer(required=False)
    creation_stats = CharacterCreationStatsSerializer(required=False)
    skills = CharacterSkillsSerializer(required=False)
    knowledge = CharacterKnowledgeSerializer(required=False)
    resources = CharacterResourcesSerializer(required=False)
    resistances = CharacterResistancesSerializer(required=False)
    statuses = CharacterStatusesSerializer(required=False)
    combat_settings = CharacterCombatSettingsSerializer(required=False)
    proficiency_points = CharacterProficiencyPointsSerializer(required=False)
    misc_data = CharacterMiscDataSerializer(required=False)

    # One-to-Many nested data for updates
    weapon_proficiencies = CharacterWeaponProficiencySerializer(many=True, required=False)
    equipment_slots = CharacterEquipmentSlotSerializer(many=True, required=False)
    learned_spells = CharacterLearnedSpellSerializer(many=True, required=False)
    attuned_spells = CharacterAttunedSpellSerializer(many=True, required=False)
    learned_spirits = CharacterLearnedSpiritSerializer(many=True, required=False)
    attuned_spirits = CharacterAttunedSpiritSerializer(many=True, required=False)
    learned_weapon_skills = CharacterLearnedWeaponSkillSerializer(many=True, required=False)
    attuned_weapon_skills = CharacterAttunedWeaponSkillSerializer(many=True, required=False)
    obtained_feats = CharacterObtainedFeatSerializer(many=True, required=False)
    companions = CharacterCompanionWriteSerializer(many=True, required=False)
    inventory_items = CharacterInventoryItemSerializer(many=True, required=False)

    class Meta:
        model = Character
        fields = [
            'name',
            'gender',
            'physical_description',
            'level',
            'souls_level',
            'background_id',
            'lineage_id',
            'bloodline_id',
            'is_finalized',
            'is_active',
            'image_url',
            # One-to-One nested data
            'stats',
            'creation_stats',
            'skills',
            'knowledge',
            'resources',
            'resistances',
            'statuses',
            'combat_settings',
            'proficiency_points',
            'misc_data',
            # One-to-Many nested data
            'weapon_proficiencies',
            'equipment_slots',
            'learned_spells',
            'attuned_spells',
            'learned_spirits',
            'attuned_spirits',
            'learned_weapon_skills',
            'attuned_weapon_skills',
            'obtained_feats',
            'companions',
            'inventory_items',
        ]

    def update(self, instance, validated_data):
        """Update character and any nested related models."""
        # Extract One-to-One nested data
        stats_data = validated_data.pop('stats', None)
        creation_stats_data = validated_data.pop('creation_stats', None)
        skills_data = validated_data.pop('skills', None)
        knowledge_data = validated_data.pop('knowledge', None)
        resources_data = validated_data.pop('resources', None)
        resistances_data = validated_data.pop('resistances', None)
        statuses_data = validated_data.pop('statuses', None)
        combat_settings_data = validated_data.pop('combat_settings', None)
        proficiency_points_data = validated_data.pop('proficiency_points', None)
        misc_data_data = validated_data.pop('misc_data', None)

        # Extract One-to-Many nested data
        weapon_proficiencies_data = validated_data.pop('weapon_proficiencies', None)
        equipment_slots_data = validated_data.pop('equipment_slots', None)
        learned_spells_data = validated_data.pop('learned_spells', None)
        attuned_spells_data = validated_data.pop('attuned_spells', None)
        learned_spirits_data = validated_data.pop('learned_spirits', None)
        attuned_spirits_data = validated_data.pop('attuned_spirits', None)
        learned_weapon_skills_data = validated_data.pop('learned_weapon_skills', None)
        attuned_weapon_skills_data = validated_data.pop('attuned_weapon_skills', None)
        obtained_feats_data = validated_data.pop('obtained_feats', None)
        companions_data = validated_data.pop('companions', None)
        inventory_items_data = validated_data.pop('inventory_items', None)

        # Update character core fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update One-to-One related models
        if stats_data is not None:
            self._update_related(instance, 'stats', CharacterStats, stats_data)

        if creation_stats_data is not None:
            self._update_related(instance, 'creation_stats', CharacterCreationStats, creation_stats_data)

        if skills_data is not None:
            self._update_related(instance, 'skills', CharacterSkills, skills_data)

        if knowledge_data is not None:
            self._update_related(instance, 'knowledge', CharacterKnowledge, knowledge_data)

        if resources_data is not None:
            self._update_related(instance, 'resources', CharacterResources, resources_data)

        if resistances_data is not None:
            self._update_related(instance, 'resistances', CharacterResistances, resistances_data)

        if statuses_data is not None:
            self._update_related(instance, 'statuses', CharacterStatuses, statuses_data)

        if combat_settings_data is not None:
            self._update_related(instance, 'combat_settings', CharacterCombatSettings, combat_settings_data)

        if proficiency_points_data is not None:
            self._update_related(instance, 'proficiency_points', CharacterProficiencyPoints, proficiency_points_data)

        if misc_data_data is not None:
            self._update_related(instance, 'misc_data', CharacterMiscData, misc_data_data)

        # Update One-to-Many related models (replace strategy)
        if weapon_proficiencies_data is not None:
            instance.weapon_proficiencies.all().delete()
            for prof_data in weapon_proficiencies_data:
                CharacterWeaponProficiency.objects.create(character=instance, **prof_data)

        if equipment_slots_data is not None:
            instance.equipment_slots.all().delete()
            for slot_data in equipment_slots_data:
                CharacterEquipmentSlot.objects.create(character=instance, **slot_data)

        if learned_spells_data is not None:
            instance.learned_spells.all().delete()
            for spell_data in learned_spells_data:
                CharacterLearnedSpell.objects.create(character=instance, **spell_data)

        if attuned_spells_data is not None:
            instance.attuned_spells.all().delete()
            for spell_data in attuned_spells_data:
                CharacterAttunedSpell.objects.create(character=instance, **spell_data)

        if learned_spirits_data is not None:
            instance.learned_spirits.all().delete()
            for spirit_data in learned_spirits_data:
                CharacterLearnedSpirit.objects.create(character=instance, **spirit_data)

        if attuned_spirits_data is not None:
            instance.attuned_spirits.all().delete()
            for spirit_data in attuned_spirits_data:
                CharacterAttunedSpirit.objects.create(character=instance, **spirit_data)

        if learned_weapon_skills_data is not None:
            instance.learned_weapon_skills.all().delete()
            for skill_data in learned_weapon_skills_data:
                CharacterLearnedWeaponSkill.objects.create(character=instance, **skill_data)

        if attuned_weapon_skills_data is not None:
            instance.attuned_weapon_skills.all().delete()
            for skill_data in attuned_weapon_skills_data:
                CharacterAttunedWeaponSkill.objects.create(character=instance, **skill_data)

        if obtained_feats_data is not None:
            instance.obtained_feats.all().delete()
            for feat_data in obtained_feats_data:
                CharacterObtainedFeat.objects.create(character=instance, **feat_data)

        if companions_data is not None:
            instance.companions.all().delete()
            for companion_data in companions_data:
                CharacterCompanion.objects.create(character=instance, **companion_data)

        if inventory_items_data is not None:
            instance.inventory_items.all().delete()
            for item_data in inventory_items_data:
                CharacterInventoryItem.objects.create(character=instance, **item_data)

        return instance

    def _update_related(self, instance, related_name, model_class, data):
        """Update or create a related One-to-One model."""
        try:
            related_obj = getattr(instance, related_name)
            for attr, value in data.items():
                setattr(related_obj, attr, value)
            related_obj.save()
        except model_class.DoesNotExist:
            model_class.objects.create(character=instance, **data)


# =============================================================================
# EQUIPMENT SLOT MANAGEMENT SERIALIZERS
# =============================================================================

class EquipmentSlotUpdateSerializer(serializers.Serializer):
    """
    Serializer for equipping/modifying items in slots.
    Used for dedicated equipment endpoints.
    """
    slot_type = serializers.ChoiceField(choices=CharacterEquipmentSlot.SLOT_CHOICES)
    item_id = serializers.IntegerField()
    item_category = serializers.ChoiceField(choices=CharacterEquipmentSlot.CATEGORY_CHOICES)
    item_name = serializers.CharField(max_length=200)
    modifications = serializers.JSONField(required=False, default=dict)


class EquipmentSlotClearSerializer(serializers.Serializer):
    """Serializer for clearing an equipment slot."""
    slot_type = serializers.ChoiceField(choices=CharacterEquipmentSlot.SLOT_CHOICES)


# =============================================================================
# SPELL/SPIRIT/SKILL MANAGEMENT SERIALIZERS
# =============================================================================

class LearnedSpellUpdateSerializer(serializers.Serializer):
    """Serializer for learning a spell."""
    spell_id = serializers.IntegerField()
    modifications = serializers.JSONField(required=False, default=dict)


class AttunedSpellUpdateSerializer(serializers.Serializer):
    """Serializer for attuning a spell."""
    spell_id = serializers.IntegerField()
    slot_number = serializers.IntegerField()


class LearnedSpiritUpdateSerializer(serializers.Serializer):
    """Serializer for learning a spirit."""
    spirit_id = serializers.IntegerField()
    modifications = serializers.JSONField(required=False, default=dict)


class AttunedSpiritUpdateSerializer(serializers.Serializer):
    """Serializer for attuning a spirit."""
    spirit_id = serializers.IntegerField()
    slot_number = serializers.IntegerField()


class LearnedWeaponSkillUpdateSerializer(serializers.Serializer):
    """Serializer for learning a weapon skill."""
    skill_id = serializers.IntegerField()
    modifications = serializers.JSONField(required=False, default=dict)


class AttunedWeaponSkillUpdateSerializer(serializers.Serializer):
    """Serializer for attuning a weapon skill."""
    skill_id = serializers.IntegerField()
    slot_number = serializers.IntegerField()


# =============================================================================
# PROFICIENCY MANAGEMENT SERIALIZERS
# =============================================================================

class WeaponProficiencyUpdateSerializer(serializers.Serializer):
    """Serializer for updating a weapon proficiency."""
    weapon_tree = serializers.ChoiceField(choices=CharacterWeaponProficiency.TREE_CHOICES)
    level = serializers.IntegerField(min_value=0, max_value=5)


class ObtainedFeatUpdateSerializer(serializers.Serializer):
    """Serializer for obtaining a feat."""
    feat_id = serializers.IntegerField()
    feat_type = serializers.ChoiceField(choices=CharacterObtainedFeat.FEAT_TYPE_CHOICES)
    weapon_tree = serializers.CharField(required=False, allow_blank=True)
    source = serializers.CharField(required=False, allow_blank=True)
    source_feat_id = serializers.IntegerField(required=False, allow_null=True)
    is_greyed_out = serializers.BooleanField(required=False, default=False)
    modifications = serializers.JSONField(required=False, default=dict)


# =============================================================================
# COMPANION SERIALIZERS
# =============================================================================

class CompanionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a companion."""

    class Meta:
        model = CharacterCompanion
        exclude = ['character']


class CompanionUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating a companion."""

    class Meta:
        model = CharacterCompanion
        exclude = ['id', 'character']


# =============================================================================
# IMPORT/EXPORT SERIALIZERS
# =============================================================================

class CharacterImportSerializer(serializers.Serializer):
    """
    Serializer for importing a character from JSON export.
    Handles the full character data structure from localStorage export.
    """

    uuid = serializers.UUIDField(required=False, allow_null=True)
    name = serializers.CharField(max_length=200)
    gender = serializers.CharField(max_length=50, required=False, allow_blank=True, default='Male')
    physical_description = serializers.CharField(required=False, allow_blank=True, default='')
    level = serializers.IntegerField(default=0)
    souls_level = serializers.IntegerField(default=0)
    background_id = serializers.IntegerField(required=True)
    lineage_id = serializers.IntegerField(required=True)
    bloodline_id = serializers.IntegerField(required=False, allow_null=True)
    is_finalized = serializers.BooleanField(default=False)
    image_url = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    # Nested data (all optional)
    stats = CharacterStatsSerializer(required=False)
    creation_stats = CharacterCreationStatsSerializer(required=False)
    skills = CharacterSkillsSerializer(required=False)
    knowledge = CharacterKnowledgeSerializer(required=False)
    resources = CharacterResourcesSerializer(required=False)
    resistances = CharacterResistancesSerializer(required=False)
    statuses = CharacterStatusesSerializer(required=False)
    combat_settings = CharacterCombatSettingsSerializer(required=False)
    proficiency_points = CharacterProficiencyPointsSerializer(required=False)
    misc_data = CharacterMiscDataSerializer(required=False)

    # One-to-Many data
    equipment_slots = CharacterEquipmentSlotSerializer(many=True, required=False)
    weapon_proficiencies = CharacterWeaponProficiencySerializer(many=True, required=False)
    learned_spells = CharacterLearnedSpellSerializer(many=True, required=False)
    attuned_spells = CharacterAttunedSpellSerializer(many=True, required=False)
    learned_spirits = CharacterLearnedSpiritSerializer(many=True, required=False)
    attuned_spirits = CharacterAttunedSpiritSerializer(many=True, required=False)
    learned_weapon_skills = CharacterLearnedWeaponSkillSerializer(many=True, required=False)
    attuned_weapon_skills = CharacterAttunedWeaponSkillSerializer(many=True, required=False)
    obtained_feats = CharacterObtainedFeatSerializer(many=True, required=False)
    companions = CharacterCompanionSerializer(many=True, required=False)

    def create(self, validated_data):
        """Create character from imported data."""
        request = self.context.get('request')
        owner = request.user.profile if request and hasattr(request.user, 'profile') else None

        if not owner:
            raise serializers.ValidationError("User profile not found")

        # Check character limit
        if not owner.can_create_character:
            raise serializers.ValidationError(
                f"Character limit reached ({owner.max_characters})"
            )

        # Extract One-to-One nested data
        stats_data = validated_data.pop('stats', {})
        creation_stats_data = validated_data.pop('creation_stats', None)
        skills_data = validated_data.pop('skills', {})
        knowledge_data = validated_data.pop('knowledge', {})
        resources_data = validated_data.pop('resources', {})
        resistances_data = validated_data.pop('resistances', {})
        statuses_data = validated_data.pop('statuses', {})
        combat_settings_data = validated_data.pop('combat_settings', {})
        proficiency_points_data = validated_data.pop('proficiency_points', {})
        misc_data_data = validated_data.pop('misc_data', {})

        # Extract One-to-Many nested data
        equipment_slots_data = validated_data.pop('equipment_slots', [])
        weapon_proficiencies_data = validated_data.pop('weapon_proficiencies', [])
        learned_spells_data = validated_data.pop('learned_spells', [])
        attuned_spells_data = validated_data.pop('attuned_spells', [])
        learned_spirits_data = validated_data.pop('learned_spirits', [])
        attuned_spirits_data = validated_data.pop('attuned_spirits', [])
        learned_weapon_skills_data = validated_data.pop('learned_weapon_skills', [])
        attuned_weapon_skills_data = validated_data.pop('attuned_weapon_skills', [])
        obtained_feats_data = validated_data.pop('obtained_feats', [])
        companions_data = validated_data.pop('companions', [])

        # Remove uuid if present (server generates a new one)
        validated_data.pop('uuid', None)

        # Create character
        validated_data['owner'] = owner
        character = Character.objects.create(**validated_data)

        # Create One-to-One models
        CharacterStats.objects.create(character=character, **stats_data)
        if creation_stats_data:
            CharacterCreationStats.objects.create(character=character, **creation_stats_data)
        CharacterSkills.objects.create(character=character, **skills_data)
        CharacterKnowledge.objects.create(character=character, **knowledge_data)
        CharacterResources.objects.create(character=character, **resources_data)
        CharacterResistances.objects.create(character=character, **resistances_data)
        CharacterStatuses.objects.create(character=character, **statuses_data)
        CharacterCombatSettings.objects.create(character=character, **combat_settings_data)
        CharacterProficiencyPoints.objects.create(character=character, **proficiency_points_data)
        CharacterMiscData.objects.create(character=character, **misc_data_data)

        # Create One-to-Many models
        for slot_data in equipment_slots_data:
            CharacterEquipmentSlot.objects.create(character=character, **slot_data)

        for prof_data in weapon_proficiencies_data:
            CharacterWeaponProficiency.objects.create(character=character, **prof_data)

        for spell_data in learned_spells_data:
            CharacterLearnedSpell.objects.create(character=character, **spell_data)

        for spell_data in attuned_spells_data:
            CharacterAttunedSpell.objects.create(character=character, **spell_data)

        for spirit_data in learned_spirits_data:
            CharacterLearnedSpirit.objects.create(character=character, **spirit_data)

        for spirit_data in attuned_spirits_data:
            CharacterAttunedSpirit.objects.create(character=character, **spirit_data)

        for skill_data in learned_weapon_skills_data:
            CharacterLearnedWeaponSkill.objects.create(character=character, **skill_data)

        for skill_data in attuned_weapon_skills_data:
            CharacterAttunedWeaponSkill.objects.create(character=character, **skill_data)

        for feat_data in obtained_feats_data:
            CharacterObtainedFeat.objects.create(character=character, **feat_data)

        for companion_data in companions_data:
            CharacterCompanion.objects.create(character=character, **companion_data)

        return character


class CharacterExportSerializer(serializers.ModelSerializer):
    """
    Serializer for exporting a character to JSON.
    Returns data in a format compatible with the Nuxt app's import function.
    """

    uuid = serializers.UUIDField(source='id', read_only=True)

    # Include all nested data
    stats = CharacterStatsSerializer(read_only=True)
    creation_stats = CharacterCreationStatsSerializer(read_only=True)
    skills = CharacterSkillsSerializer(read_only=True)
    knowledge = CharacterKnowledgeSerializer(read_only=True)
    resources = CharacterResourcesSerializer(read_only=True)
    resistances = CharacterResistancesSerializer(read_only=True)
    statuses = CharacterStatusesSerializer(read_only=True)
    combat_settings = CharacterCombatSettingsSerializer(read_only=True)
    proficiency_points = CharacterProficiencyPointsSerializer(read_only=True)
    misc_data = CharacterMiscDataSerializer(read_only=True)
    equipment_slots = CharacterEquipmentSlotSerializer(many=True, read_only=True)
    weapon_proficiencies = CharacterWeaponProficiencySerializer(many=True, read_only=True)
    learned_spells = CharacterLearnedSpellSerializer(many=True, read_only=True)
    attuned_spells = CharacterAttunedSpellSerializer(many=True, read_only=True)
    learned_spirits = CharacterLearnedSpiritSerializer(many=True, read_only=True)
    attuned_spirits = CharacterAttunedSpiritSerializer(many=True, read_only=True)
    learned_weapon_skills = CharacterLearnedWeaponSkillSerializer(many=True, read_only=True)
    attuned_weapon_skills = CharacterAttunedWeaponSkillSerializer(many=True, read_only=True)
    obtained_feats = CharacterObtainedFeatSerializer(many=True, read_only=True)
    companions = CharacterCompanionSerializer(many=True, read_only=True)

    class Meta:
        model = Character
        fields = [
            'uuid',
            'name',
            'gender',
            'physical_description',
            'level',
            'souls_level',
            'background_id',
            'lineage_id',
            'bloodline_id',
            'is_finalized',
            'image_url',
            'created_at',
            'last_played',
            # Nested data
            'stats',
            'creation_stats',
            'skills',
            'knowledge',
            'resources',
            'resistances',
            'statuses',
            'combat_settings',
            'proficiency_points',
            'misc_data',
            'equipment_slots',
            'weapon_proficiencies',
            'learned_spells',
            'attuned_spells',
            'learned_spirits',
            'attuned_spirits',
            'learned_weapon_skills',
            'attuned_weapon_skills',
            'obtained_feats',
            'companions',
        ]
