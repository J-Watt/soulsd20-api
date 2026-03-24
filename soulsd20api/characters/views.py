"""
Views for normalized character API.

Provides endpoints for character CRUD operations with optimized
queries for the normalized database structure.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone

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
)
from .serializers import (
    CharacterListSerializer,
    CharacterDetailSerializer,
    CharacterCreateSerializer,
    CharacterUpdateSerializer,
    CharacterImportSerializer,
    CharacterExportSerializer,
    EquipmentSlotUpdateSerializer,
    EquipmentSlotClearSerializer,
    WeaponProficiencyUpdateSerializer,
    LearnedSpellUpdateSerializer,
    AttunedSpellUpdateSerializer,
    LearnedSpiritUpdateSerializer,
    AttunedSpiritUpdateSerializer,
    LearnedWeaponSkillUpdateSerializer,
    AttunedWeaponSkillUpdateSerializer,
    ObtainedFeatUpdateSerializer,
    CompanionCreateSerializer,
    CompanionUpdateSerializer,
    CharacterCompanionSerializer,
)


class CharacterViewSet(viewsets.ModelViewSet):
    """
    ViewSet for character CRUD operations.

    Endpoints:
    - GET    /api/characters/                    - List user's characters
    - POST   /api/characters/                    - Create character
    - GET    /api/characters/{id}/               - Get character detail
    - PATCH  /api/characters/{id}/               - Update character
    - DELETE /api/characters/{id}/               - Soft delete character
    - POST   /api/characters/import/             - Import character from JSON
    - GET    /api/characters/{id}/export/        - Export character to JSON
    - POST   /api/characters/{id}/equip/         - Equip item to slot
    - POST   /api/characters/{id}/unequip/       - Clear equipment slot
    - POST   /api/characters/{id}/proficiency/   - Update weapon proficiency
    - POST   /api/characters/{id}/spell/learn/   - Learn a spell
    - POST   /api/characters/{id}/spell/attune/  - Attune a spell
    - POST   /api/characters/{id}/spell/unlearn/ - Unlearn a spell
    - POST   /api/characters/{id}/spirit/learn/  - Learn a spirit
    - POST   /api/characters/{id}/spirit/attune/ - Attune a spirit
    - POST   /api/characters/{id}/skill/learn/   - Learn a weapon skill
    - POST   /api/characters/{id}/skill/attune/  - Attune a weapon skill
    - POST   /api/characters/{id}/feat/          - Obtain a feat
    - GET    /api/characters/{id}/companions/    - List companions
    - POST   /api/characters/{id}/companions/    - Create companion
    - POST   /api/characters/{id}/upload-image/  - Upload character portrait
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    lookup_field = 'id'

    def get_queryset(self):
        """
        Return characters owned by the current user.
        Admins can see all characters.
        Uses select_related and prefetch_related for optimization.
        """
        user = self.request.user

        if not hasattr(user, 'profile'):
            return Character.objects.none()

        profile = user.profile

        # own_only=true forces owner filter even for admins (used by dashboard)
        own_only = self.request.query_params.get('own_only', 'false')

        if profile.is_admin and own_only.lower() != 'true':
            # Admins can see all characters (for admin tools)
            queryset = Character.objects.all()
        else:
            # Regular users (or admin with own_only) see only their own characters
            queryset = Character.objects.filter(owner=profile)

        # Filter by active status (default: only active)
        show_inactive = self.request.query_params.get('show_inactive', 'false')
        if show_inactive.lower() != 'true':
            queryset = queryset.filter(is_active=True)

        # Optimize queries based on action
        if self.action in ['retrieve', 'export_character']:
            # Full detail view - fetch everything
            queryset = queryset.select_related(
                'owner',
                'owner__user',
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
            ).prefetch_related(
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
            )
        elif self.action == 'list':
            # List also needs full data for character sync
            queryset = queryset.select_related(
                'owner',
                'owner__user',
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
            ).prefetch_related(
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
            )

        return queryset

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            # Use detail serializer for list to include all nested data
            # Character sync needs full data to populate localStorage correctly
            return CharacterDetailSerializer
        elif self.action == 'create':
            return CharacterCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return CharacterUpdateSerializer
        elif self.action == 'export_character':
            return CharacterExportSerializer
        elif self.action == 'import_character':
            return CharacterImportSerializer
        return CharacterDetailSerializer

    def partial_update(self, request, *args, **kwargs):
        """
        PATCH update with detailed error logging.
        """
        import logging
        logger = logging.getLogger('characters')

        instance = self.get_object()
        print(f'[SD20 API] partial_update: character="{instance.name}" (id={instance.id}), fields={list(request.data.keys())}')
        serializer = self.get_serializer(instance, data=request.data, partial=True)

        if not serializer.is_valid():
            # Print to stdout so it shows in dev server terminal
            print(f'\n[PATCH ERROR] Character: {instance.name} ({instance.id})')
            print(f'[PATCH ERROR] Validation errors: {serializer.errors}\n')
            logger.error(
                f'Character PATCH validation failed for {instance.name} ({instance.id}): '
                f'{serializer.errors}'
            )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            self.perform_update(serializer)
        except Exception as e:
            logger.error(
                f'Character PATCH update error for {instance.name} ({instance.id}): {e}',
                exc_info=True
            )
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(CharacterDetailSerializer(instance).data)

    def create(self, request, *args, **kwargs):
        """
        Create a new character.
        Checks character limit before creation.
        """
        profile = request.user.profile
        print(f'[SD20 API] create: user="{request.user.username}", name="{request.data.get("name", "N/A")}", uuid="{request.data.get("uuid", "N/A")}"')

        # Check character limit
        if not profile.can_create_character:
            print(f'[SD20 API] create: DENIED - character limit reached ({profile.max_characters})')
            return Response(
                {'error': f'Character limit reached ({profile.max_characters})'},
                status=status.HTTP_403_FORBIDDEN
            )

        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        """Set the owner when creating a character."""
        serializer.save(owner=self.request.user.profile)

    def destroy(self, request, *args, **kwargs):
        """
        Hard delete a character and all related data.
        Django CASCADE handles related One-to-One and One-to-Many records.
        Also cleans up the character's image file if one exists.
        """
        instance = self.get_object()
        print(f'[SD20 API] destroy: deleting character="{instance.name}" (id={instance.id})')

        # Clean up image file
        self._delete_image_file(instance)

        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'], url_path='upload-image',
            parser_classes=[MultiPartParser, FormParser])
    def upload_image(self, request, **kwargs):
        """
        Upload a character portrait image.
        POST /api/characters/{uuid}/upload-image/
        Rate limited: 3 uploads per 24 hours per character.
        """
        from django.core.cache import cache
        from django.conf import settings
        from PIL import Image as PILImage
        import io
        import os

        instance = self.get_object()

        # Rate limiting: 3 uploads per 24 hours per character
        cache_key = f'img_upload_{instance.id}'
        upload_count = cache.get(cache_key, 0)
        if upload_count >= 3:
            return Response(
                {'detail': 'Upload limit reached (3 per 24 hours). Try again later.'},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        # Get uploaded file
        image_file = request.FILES.get('image')
        if not image_file:
            return Response(
                {'detail': 'No image file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate file type
        allowed_types = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']
        if image_file.content_type not in allowed_types:
            return Response(
                {'detail': f'Invalid file type: {image_file.content_type}. Allowed: JPEG, PNG, WebP, GIF'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate file size (5MB max)
        if image_file.size > 5 * 1024 * 1024:
            return Response(
                {'detail': 'File too large. Maximum size is 5MB.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Open and resize image
            img = PILImage.open(image_file)

            # Convert RGBA/P to RGB for JPEG output
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')

            # Resize to max 512x512, preserving aspect ratio
            img.thumbnail((512, 512), PILImage.LANCZOS)

            # Delete old file if it exists (replacing image)
            self._delete_image_file(instance)

            # Save to buffer
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=85)
            buffer.seek(0)

            filename = f'character_images/{instance.id}.jpg'

            if settings.USE_CLOUD_STORAGE:
                # Upload to Cloudflare R2 via boto3
                import boto3
                s3 = boto3.client(
                    's3',
                    endpoint_url=settings.AWS_S3_ENDPOINT_URL,
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                )
                s3.put_object(
                    Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                    Key=filename,
                    Body=buffer.read(),
                    ContentType='image/jpeg',
                )
                image_url = f'https://{settings.AWS_S3_CUSTOM_DOMAIN}/{filename}'
            else:
                # Local filesystem (development)
                media_dir = os.path.join(settings.MEDIA_ROOT, 'character_images')
                os.makedirs(media_dir, exist_ok=True)
                filepath = os.path.join(media_dir, f'{instance.id}.jpg')
                with open(filepath, 'wb') as f:
                    f.write(buffer.read())
                image_url = f'{settings.MEDIA_URL}{filename}'

            # Update character's image_url field
            instance.image_url = image_url
            instance.save(update_fields=['image_url'])

            # Increment rate limit counter (24 hour TTL)
            cache.set(cache_key, upload_count + 1, 24 * 60 * 60)

            print(f'[SD20 API] upload_image: saved portrait for "{instance.name}" -> {image_url}')

            return Response({
                'image_url': image_url,
                'message': f'Image uploaded ({3 - upload_count - 1} uploads remaining today)'
            })

        except Exception as e:
            print(f'[SD20 API] upload_image error: {e}')
            return Response(
                {'detail': f'Failed to process image: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    def _delete_image_file(self, instance):
        """Delete the character's image file from storage."""
        from django.conf import settings

        if not instance.image_url:
            return

        if settings.USE_CLOUD_STORAGE and 'r2.dev' in str(instance.image_url):
            # Delete from R2
            try:
                import boto3
                s3 = boto3.client(
                    's3',
                    endpoint_url=settings.AWS_S3_ENDPOINT_URL,
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                )
                key = f'character_images/{instance.id}.jpg'
                s3.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=key)
                print(f'[SD20 API] Deleted image from R2: {key}')
            except Exception as e:
                print(f'[SD20 API] Failed to delete image from R2: {e}')
        elif 'character_images/' in str(instance.image_url):
            # Delete from local filesystem
            import os
            filepath = os.path.join(
                settings.MEDIA_ROOT,
                'character_images',
                f'{instance.id}.jpg'
            )
            if os.path.exists(filepath):
                os.remove(filepath)
                print(f'[SD20 API] Deleted image file: {filepath}')

    @action(detail=False, methods=['post'], url_path='import')
    def import_character(self, request):
        """
        Import a character from JSON export.
        POST /api/characters/import/

        Request body: Full character data JSON
        """
        serializer = CharacterImportSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            character = serializer.save()
            # Refresh with full relations for response
            character = Character.objects.select_related(
                'owner', 'stats', 'skills', 'knowledge',
                'resources', 'resistances', 'statuses',
                'combat_settings', 'proficiency_points', 'misc_data'
            ).prefetch_related(
                'equipment_slots', 'weapon_proficiencies',
                'learned_spells', 'attuned_spells',
                'learned_spirits', 'attuned_spirits',
                'learned_weapon_skills', 'attuned_weapon_skills',
                'obtained_feats', 'companions'
            ).get(id=character.id)
            return Response(
                CharacterDetailSerializer(character).data,
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], url_path='export')
    def export_character(self, request, id=None):
        """
        Export a character to JSON.
        GET /api/characters/{id}/export/

        Returns: Full character data in export-compatible format
        """
        character = self.get_object()
        serializer = CharacterExportSerializer(character)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='update-last-played')
    def update_last_played(self, request, id=None):
        """
        Update the last_played timestamp.
        POST /api/characters/{id}/update-last-played/

        Called when a character is selected/played.
        """
        character = self.get_object()
        character.last_played = timezone.now()
        character.save(update_fields=['last_played'])
        return Response({'last_played': character.last_played.isoformat()})

    @action(detail=True, methods=['post'], url_path='restore')
    def restore_character(self, request, id=None):
        """
        Restore a soft-deleted character.
        POST /api/characters/{id}/restore/
        """
        # Include inactive characters in this query
        character = Character.objects.filter(
            id=id,
            owner=request.user.profile
        ).first()

        if not character:
            return Response(
                {'error': 'Character not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check character limit before restoring
        if not request.user.profile.can_create_character:
            return Response(
                {'error': f'Character limit reached ({request.user.profile.max_characters})'},
                status=status.HTTP_403_FORBIDDEN
            )

        character.is_active = True
        character.save(update_fields=['is_active'])

        return Response(CharacterDetailSerializer(character).data)

    @action(detail=True, methods=['delete'], url_path='permanent-delete')
    def permanent_delete(self, request, id=None):
        """
        Permanently delete a character (cannot be undone).
        DELETE /api/characters/{id}/permanent-delete/

        Only available for already soft-deleted characters.
        """
        character = Character.objects.filter(
            id=id,
            owner=request.user.profile,
            is_active=False  # Can only permanently delete inactive characters
        ).first()

        if not character:
            return Response(
                {'error': 'Character not found or not eligible for permanent deletion'},
                status=status.HTTP_404_NOT_FOUND
            )

        character.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # =========================================================================
    # EQUIPMENT MANAGEMENT
    # =========================================================================

    @action(detail=True, methods=['post'], url_path='equip')
    def equip_item(self, request, id=None):
        """
        Equip an item to a slot.
        POST /api/characters/{id}/equip/

        Request body: { slot_type, item_id, item_category, item_name, modifications? }
        """
        character = self.get_object()
        serializer = EquipmentSlotUpdateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        slot_type = data['slot_type']

        # Update or create equipment slot
        slot, created = CharacterEquipmentSlot.objects.update_or_create(
            character=character,
            slot_type=slot_type,
            defaults={
                'item_id': data['item_id'],
                'item_category': data['item_category'],
                'item_name': data['item_name'],
                'modifications': data.get('modifications', {}),
            }
        )

        return Response({
            'slot_type': slot.slot_type,
            'item_id': slot.item_id,
            'item_category': slot.item_category,
            'item_name': slot.item_name,
            'modifications': slot.modifications,
        }, status=status.HTTP_200_OK if not created else status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='unequip')
    def unequip_item(self, request, id=None):
        """
        Clear an equipment slot.
        POST /api/characters/{id}/unequip/

        Request body: { slot_type }
        """
        character = self.get_object()
        serializer = EquipmentSlotClearSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        slot_type = serializer.validated_data['slot_type']
        deleted, _ = CharacterEquipmentSlot.objects.filter(
            character=character,
            slot_type=slot_type
        ).delete()

        if deleted:
            return Response({'message': f'{slot_type} slot cleared'})
        return Response(
            {'error': f'{slot_type} slot was already empty'},
            status=status.HTTP_404_NOT_FOUND
        )

    # =========================================================================
    # WEAPON PROFICIENCY MANAGEMENT
    # =========================================================================

    @action(detail=True, methods=['post'], url_path='proficiency')
    def update_proficiency(self, request, id=None):
        """
        Update a weapon proficiency level.
        POST /api/characters/{id}/proficiency/

        Request body: { weapon_tree, level }
        """
        character = self.get_object()
        serializer = WeaponProficiencyUpdateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        prof, created = CharacterWeaponProficiency.objects.update_or_create(
            character=character,
            weapon_tree=data['weapon_tree'],
            defaults={'level': data['level']}
        )

        return Response({
            'weapon_tree': prof.weapon_tree,
            'level': prof.level,
        })

    # =========================================================================
    # SPELL MANAGEMENT
    # =========================================================================

    @action(detail=True, methods=['post'], url_path='spell/learn')
    def learn_spell(self, request, id=None):
        """Learn a spell. POST /api/characters/{id}/spell/learn/"""
        character = self.get_object()
        serializer = LearnedSpellUpdateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        spell, created = CharacterLearnedSpell.objects.update_or_create(
            character=character,
            spell_id=data['spell_id'],
            defaults={'modifications': data.get('modifications', {})}
        )

        return Response({
            'spell_id': spell.spell_id,
            'modifications': spell.modifications,
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='spell/unlearn')
    def unlearn_spell(self, request, id=None):
        """Unlearn a spell. POST /api/characters/{id}/spell/unlearn/"""
        character = self.get_object()
        spell_id = request.data.get('spell_id')

        if not spell_id:
            return Response({'error': 'spell_id required'}, status=status.HTTP_400_BAD_REQUEST)

        # Also remove from attuned
        CharacterAttunedSpell.objects.filter(character=character, spell_id=spell_id).delete()
        deleted, _ = CharacterLearnedSpell.objects.filter(
            character=character,
            spell_id=spell_id
        ).delete()

        if deleted:
            return Response({'message': f'Spell {spell_id} unlearned'})
        return Response({'error': 'Spell not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'], url_path='spell/attune')
    def attune_spell(self, request, id=None):
        """Attune a spell. POST /api/characters/{id}/spell/attune/"""
        character = self.get_object()
        serializer = AttunedSpellUpdateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        # Verify spell is learned
        if not CharacterLearnedSpell.objects.filter(
            character=character,
            spell_id=data['spell_id']
        ).exists():
            return Response(
                {'error': 'Spell must be learned first'},
                status=status.HTTP_400_BAD_REQUEST
            )

        attuned, created = CharacterAttunedSpell.objects.update_or_create(
            character=character,
            slot_number=data['slot_number'],
            defaults={'spell_id': data['spell_id']}
        )

        return Response({
            'spell_id': attuned.spell_id,
            'slot_number': attuned.slot_number,
        })

    @action(detail=True, methods=['post'], url_path='spell/unattune')
    def unattune_spell(self, request, id=None):
        """Unattune a spell. POST /api/characters/{id}/spell/unattune/"""
        character = self.get_object()
        slot_number = request.data.get('slot_number')

        if slot_number is None:
            return Response({'error': 'slot_number required'}, status=status.HTTP_400_BAD_REQUEST)

        deleted, _ = CharacterAttunedSpell.objects.filter(
            character=character,
            slot_number=slot_number
        ).delete()

        if deleted:
            return Response({'message': f'Spell slot {slot_number} cleared'})
        return Response({'error': 'Slot was already empty'}, status=status.HTTP_404_NOT_FOUND)

    # =========================================================================
    # SPIRIT MANAGEMENT
    # =========================================================================

    @action(detail=True, methods=['post'], url_path='spirit/learn')
    def learn_spirit(self, request, id=None):
        """Learn a spirit. POST /api/characters/{id}/spirit/learn/"""
        character = self.get_object()
        serializer = LearnedSpiritUpdateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        spirit, created = CharacterLearnedSpirit.objects.update_or_create(
            character=character,
            spirit_id=data['spirit_id'],
            defaults={'modifications': data.get('modifications', {})}
        )

        return Response({
            'spirit_id': spirit.spirit_id,
            'modifications': spirit.modifications,
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='spirit/unlearn')
    def unlearn_spirit(self, request, id=None):
        """Unlearn a spirit. POST /api/characters/{id}/spirit/unlearn/"""
        character = self.get_object()
        spirit_id = request.data.get('spirit_id')

        if not spirit_id:
            return Response({'error': 'spirit_id required'}, status=status.HTTP_400_BAD_REQUEST)

        CharacterAttunedSpirit.objects.filter(character=character, spirit_id=spirit_id).delete()
        deleted, _ = CharacterLearnedSpirit.objects.filter(
            character=character,
            spirit_id=spirit_id
        ).delete()

        if deleted:
            return Response({'message': f'Spirit {spirit_id} unlearned'})
        return Response({'error': 'Spirit not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'], url_path='spirit/attune')
    def attune_spirit(self, request, id=None):
        """Attune a spirit. POST /api/characters/{id}/spirit/attune/"""
        character = self.get_object()
        serializer = AttunedSpiritUpdateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        if not CharacterLearnedSpirit.objects.filter(
            character=character,
            spirit_id=data['spirit_id']
        ).exists():
            return Response(
                {'error': 'Spirit must be learned first'},
                status=status.HTTP_400_BAD_REQUEST
            )

        attuned, created = CharacterAttunedSpirit.objects.update_or_create(
            character=character,
            slot_number=data['slot_number'],
            defaults={'spirit_id': data['spirit_id']}
        )

        return Response({
            'spirit_id': attuned.spirit_id,
            'slot_number': attuned.slot_number,
        })

    @action(detail=True, methods=['post'], url_path='spirit/unattune')
    def unattune_spirit(self, request, id=None):
        """Unattune a spirit. POST /api/characters/{id}/spirit/unattune/"""
        character = self.get_object()
        slot_number = request.data.get('slot_number')

        if slot_number is None:
            return Response({'error': 'slot_number required'}, status=status.HTTP_400_BAD_REQUEST)

        deleted, _ = CharacterAttunedSpirit.objects.filter(
            character=character,
            slot_number=slot_number
        ).delete()

        if deleted:
            return Response({'message': f'Spirit slot {slot_number} cleared'})
        return Response({'error': 'Slot was already empty'}, status=status.HTTP_404_NOT_FOUND)

    # =========================================================================
    # WEAPON SKILL MANAGEMENT
    # =========================================================================

    @action(detail=True, methods=['post'], url_path='weapon-skill/learn')
    def learn_weapon_skill(self, request, id=None):
        """Learn a weapon skill. POST /api/characters/{id}/weapon-skill/learn/"""
        character = self.get_object()
        serializer = LearnedWeaponSkillUpdateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        skill, created = CharacterLearnedWeaponSkill.objects.update_or_create(
            character=character,
            skill_id=data['skill_id'],
            defaults={'modifications': data.get('modifications', {})}
        )

        return Response({
            'skill_id': skill.skill_id,
            'modifications': skill.modifications,
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='weapon-skill/unlearn')
    def unlearn_weapon_skill(self, request, id=None):
        """Unlearn a weapon skill. POST /api/characters/{id}/weapon-skill/unlearn/"""
        character = self.get_object()
        skill_id = request.data.get('skill_id')

        if not skill_id:
            return Response({'error': 'skill_id required'}, status=status.HTTP_400_BAD_REQUEST)

        CharacterAttunedWeaponSkill.objects.filter(character=character, skill_id=skill_id).delete()
        deleted, _ = CharacterLearnedWeaponSkill.objects.filter(
            character=character,
            skill_id=skill_id
        ).delete()

        if deleted:
            return Response({'message': f'Weapon skill {skill_id} unlearned'})
        return Response({'error': 'Weapon skill not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'], url_path='weapon-skill/attune')
    def attune_weapon_skill(self, request, id=None):
        """Attune a weapon skill. POST /api/characters/{id}/weapon-skill/attune/"""
        character = self.get_object()
        serializer = AttunedWeaponSkillUpdateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        if not CharacterLearnedWeaponSkill.objects.filter(
            character=character,
            skill_id=data['skill_id']
        ).exists():
            return Response(
                {'error': 'Weapon skill must be learned first'},
                status=status.HTTP_400_BAD_REQUEST
            )

        attuned, created = CharacterAttunedWeaponSkill.objects.update_or_create(
            character=character,
            slot_number=data['slot_number'],
            defaults={'skill_id': data['skill_id']}
        )

        return Response({
            'skill_id': attuned.skill_id,
            'slot_number': attuned.slot_number,
        })

    @action(detail=True, methods=['post'], url_path='weapon-skill/unattune')
    def unattune_weapon_skill(self, request, id=None):
        """Unattune a weapon skill. POST /api/characters/{id}/weapon-skill/unattune/"""
        character = self.get_object()
        slot_number = request.data.get('slot_number')

        if slot_number is None:
            return Response({'error': 'slot_number required'}, status=status.HTTP_400_BAD_REQUEST)

        deleted, _ = CharacterAttunedWeaponSkill.objects.filter(
            character=character,
            slot_number=slot_number
        ).delete()

        if deleted:
            return Response({'message': f'Weapon skill slot {slot_number} cleared'})
        return Response({'error': 'Slot was already empty'}, status=status.HTTP_404_NOT_FOUND)

    # =========================================================================
    # FEAT MANAGEMENT
    # =========================================================================

    @action(detail=True, methods=['post'], url_path='feat')
    def obtain_feat(self, request, id=None):
        """Obtain a feat. POST /api/characters/{id}/feat/"""
        character = self.get_object()
        serializer = ObtainedFeatUpdateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        feat = CharacterObtainedFeat.objects.create(
            character=character,
            **data
        )

        return Response({
            'feat_id': feat.feat_id,
            'feat_type': feat.feat_type,
            'weapon_tree': feat.weapon_tree,
            'source': feat.source,
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'], url_path='feat/(?P<feat_id>[0-9]+)')
    def remove_feat(self, request, id=None, feat_id=None):
        """Remove a feat. DELETE /api/characters/{id}/feat/{feat_id}/"""
        character = self.get_object()
        deleted, _ = CharacterObtainedFeat.objects.filter(
            character=character,
            feat_id=int(feat_id)
        ).delete()

        if deleted:
            return Response({'message': f'Feat {feat_id} removed'})
        return Response({'error': 'Feat not found'}, status=status.HTTP_404_NOT_FOUND)

    # =========================================================================
    # COMPANION MANAGEMENT
    # =========================================================================

    @action(detail=True, methods=['get', 'post'], url_path='companions')
    def companions_list(self, request, id=None):
        """
        List or create companions.
        GET /api/characters/{id}/companions/
        POST /api/characters/{id}/companions/
        """
        character = self.get_object()

        if request.method == 'GET':
            companions = character.companions.all()
            serializer = CharacterCompanionSerializer(companions, many=True)
            return Response(serializer.data)

        elif request.method == 'POST':
            serializer = CompanionCreateSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            companion = CharacterCompanion.objects.create(
                character=character,
                **serializer.validated_data
            )
            return Response(
                CharacterCompanionSerializer(companion).data,
                status=status.HTTP_201_CREATED
            )

    @action(detail=True, methods=['patch', 'delete'], url_path='companions/(?P<companion_id>[0-9a-f-]+)')
    def companion_detail(self, request, id=None, companion_id=None):
        """
        Update or delete a companion.
        PATCH /api/characters/{id}/companions/{companion_id}/
        DELETE /api/characters/{id}/companions/{companion_id}/
        """
        character = self.get_object()

        try:
            companion = CharacterCompanion.objects.get(
                id=companion_id,
                character=character
            )
        except CharacterCompanion.DoesNotExist:
            return Response({'error': 'Companion not found'}, status=status.HTTP_404_NOT_FOUND)

        if request.method == 'DELETE':
            companion.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        elif request.method == 'PATCH':
            serializer = CompanionUpdateSerializer(companion, data=request.data, partial=True)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response(CharacterCompanionSerializer(companion).data)
