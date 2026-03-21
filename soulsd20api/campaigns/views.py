"""
Campaign Views for SD20 API.

Provides ViewSets and views for campaign management.
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import Campaign, CampaignMembership, CampaignInvite
from .serializers import (
    CampaignListSerializer,
    CampaignDetailSerializer,
    CampaignCreateSerializer,
    CampaignUpdateSerializer,
    CampaignMembershipSerializer,
    CampaignInviteSerializer,
    CampaignInviteCreateSerializer,
    JoinCampaignSerializer,
    AssignCharacterSerializer,
)


class IsGMOrReadOnly(permissions.BasePermission):
    """Only the GM can modify the campaign."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.gm == request.user.profile


class CampaignViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Campaign CRUD operations.

    list: Get all campaigns the user is part of (as GM or member)
    create: Create a new campaign (user becomes GM)
    retrieve: Get campaign details
    update/partial_update: Update campaign (GM only)
    destroy: Delete campaign (GM only)
    """
    permission_classes = [permissions.IsAuthenticated, IsGMOrReadOnly]

    def get_queryset(self):
        """Get campaigns where user is GM or member."""
        user_profile = self.request.user.profile
        from django.db.models import Q

        return Campaign.objects.filter(
            Q(gm=user_profile) |
            Q(memberships__user=user_profile, memberships__status='active')
        ).distinct().select_related('gm__user').prefetch_related('memberships__user__user')

    def get_serializer_class(self):
        if self.action == 'create':
            return CampaignCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return CampaignUpdateSerializer
        elif self.action == 'retrieve':
            return CampaignDetailSerializer
        return CampaignListSerializer

    def perform_create(self, serializer):
        # Check if user can create more campaigns (Patreon tier limit)
        user_profile = self.request.user.profile
        current_count = Campaign.objects.filter(gm=user_profile).count()
        if current_count >= user_profile.max_campaigns_as_gm:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied(
                f"You can only create {user_profile.max_campaigns_as_gm} campaigns. "
                "Upgrade your Patreon tier for more."
            )
        serializer.save()

    @action(detail=False, methods=['get'])
    def as_gm(self, request):
        """Get campaigns where user is the GM."""
        campaigns = Campaign.objects.filter(gm=request.user.profile)
        serializer = CampaignListSerializer(campaigns, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def as_player(self, request):
        """Get campaigns where user is a player."""
        campaigns = Campaign.objects.filter(
            memberships__user=request.user.profile,
            memberships__status='active'
        ).exclude(gm=request.user.profile)
        serializer = CampaignListSerializer(campaigns, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def join(self, request):
        """Join a campaign using an invite code."""
        serializer = JoinCampaignSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        campaign = serializer.validated_data['invite_code']
        user_profile = request.user.profile

        # Check if user is the GM (can't join own campaign as player)
        if campaign.gm == user_profile:
            return Response(
                {'detail': 'You cannot join your own campaign as a player'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if already a member
        existing = CampaignMembership.objects.filter(
            campaign=campaign,
            user=user_profile
        ).first()

        if existing:
            if existing.status == 'active':
                return Response(
                    {'detail': 'You are already a member of this campaign'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            # Rejoin if previously left
            existing.status = 'active'
            existing.save()
            membership = existing
        else:
            membership = CampaignMembership.objects.create(
                campaign=campaign,
                user=user_profile,
                role='player',
                status='active'
            )

        return Response({
            'detail': f'Successfully joined {campaign.name}',
            'campaign': CampaignDetailSerializer(campaign).data,
            'membership': CampaignMembershipSerializer(membership).data
        })

    @action(detail=True, methods=['post'])
    def regenerate_invite(self, request, pk=None):
        """Regenerate the campaign invite code (GM only)."""
        campaign = self.get_object()
        new_code = campaign.regenerate_invite_code()
        return Response({'invite_code': new_code})

    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        """Leave a campaign."""
        campaign = self.get_object()
        user_profile = request.user.profile

        if campaign.gm == user_profile:
            return Response(
                {'detail': 'GM cannot leave their own campaign. Transfer ownership or delete it.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        membership = get_object_or_404(
            CampaignMembership,
            campaign=campaign,
            user=user_profile,
            status='active'
        )
        membership.status = 'left'
        membership.save()

        # Unassign user's characters from this campaign
        from characters.models import Character
        Character.objects.filter(
            owner=user_profile,
            campaign=campaign
        ).update(campaign=None)

        return Response({'detail': f'You have left {campaign.name}'})

    @action(detail=True, methods=['get'])
    def characters(self, request, pk=None):
        """Get all characters assigned to this campaign via M2M."""
        campaign = self.get_object()
        from characters.models import Character, CharacterCampaignMembership
        from characters.serializers import CharacterListSerializer

        # Get character IDs from M2M membership table
        char_ids = CharacterCampaignMembership.objects.filter(
            campaign=campaign,
            is_active=True
        ).values_list('character_id', flat=True)

        characters = Character.objects.filter(
            id__in=char_ids,
            is_active=True
        ).select_related('owner__user')

        serializer = CharacterListSerializer(characters, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def assign_character(self, request, pk=None):
        """Assign a character to this campaign (multi-campaign M2M)."""
        campaign = self.get_object()
        user_profile = request.user.profile

        # Only the character owner can assign (not GMs)
        serializer = AssignCharacterSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        character = serializer.validated_data['character_uuid']

        # Verify the user owns this character
        if character.owner != user_profile:
            return Response(
                {'detail': 'You can only assign your own characters'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Verify user is a member of this campaign
        is_member = (
            campaign.gm == user_profile or
            CampaignMembership.objects.filter(
                campaign=campaign,
                user=user_profile,
                status='active'
            ).exists()
        )

        if not is_member:
            return Response(
                {'detail': 'You are not a member of this campaign'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Create M2M membership (or reactivate if previously removed)
        from characters.models import CharacterCampaignMembership
        membership, created = CharacterCampaignMembership.objects.get_or_create(
            character=character,
            campaign=campaign,
            defaults={'is_active': True}
        )
        if not created and not membership.is_active:
            membership.is_active = True
            membership.save(update_fields=['is_active'])

        return Response({
            'detail': f'{character.name} has been assigned to {campaign.name}',
            'character_id': str(character.id),
            'campaign_id': str(campaign.id)
        })

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def unassign_character(self, request, pk=None):
        """Remove a character from this campaign."""
        campaign = self.get_object()
        serializer = AssignCharacterSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        character = serializer.validated_data['character_uuid']

        from characters.models import CharacterCampaignMembership
        membership = CharacterCampaignMembership.objects.filter(
            character=character,
            campaign=campaign,
            is_active=True
        ).first()

        if not membership:
            return Response(
                {'detail': 'Character is not in this campaign'},
                status=status.HTTP_400_BAD_REQUEST
            )

        membership.is_active = False
        membership.save(update_fields=['is_active'])

        return Response({
            'detail': f'{character.name} has been removed from {campaign.name}'
        })


class CampaignMembershipViewSet(viewsets.ModelViewSet):
    """ViewSet for managing campaign memberships (GM only)."""
    serializer_class = CampaignMembershipSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        campaign_id = self.kwargs.get('campaign_pk')
        return CampaignMembership.objects.filter(
            campaign_id=campaign_id
        ).select_related('user__user')

    def get_campaign(self):
        campaign_id = self.kwargs.get('campaign_pk')
        return get_object_or_404(Campaign, pk=campaign_id)

    def check_gm_permission(self):
        campaign = self.get_campaign()
        if campaign.gm != self.request.user.profile:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only the GM can manage memberships")

    @action(detail=True, methods=['post'])
    def kick(self, request, campaign_pk=None, pk=None):
        """Kick a member from the campaign."""
        self.check_gm_permission()
        membership = self.get_object()

        if membership.user == self.get_campaign().gm:
            return Response(
                {'detail': 'Cannot kick the GM'},
                status=status.HTTP_400_BAD_REQUEST
            )

        membership.status = 'kicked'
        membership.save()

        # Unassign their characters
        from characters.models import Character
        Character.objects.filter(
            owner=membership.user,
            campaign=self.get_campaign()
        ).update(campaign=None)

        return Response({'detail': f'{membership.user.user.username} has been kicked'})


class CampaignInviteViewSet(viewsets.ModelViewSet):
    """ViewSet for direct campaign invites."""
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_profile = self.request.user.profile
        return CampaignInvite.objects.filter(
            invited_user=user_profile,
            status='pending'
        ).select_related('campaign', 'invited_by__user')

    def get_serializer_class(self):
        if self.action == 'create':
            return CampaignInviteCreateSerializer
        return CampaignInviteSerializer

    @action(detail=False, methods=['get'])
    def sent(self, request):
        """Get invites sent by the user."""
        invites = CampaignInvite.objects.filter(
            invited_by=request.user.profile
        ).select_related('campaign', 'invited_user__user')
        serializer = CampaignInviteSerializer(invites, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """Accept an invite."""
        invite = self.get_object()

        if invite.invited_user != request.user.profile:
            return Response(
                {'detail': 'This invite is not for you'},
                status=status.HTTP_403_FORBIDDEN
            )

        membership = invite.accept()
        if membership:
            return Response({
                'detail': f'You have joined {invite.campaign.name}',
                'campaign': CampaignListSerializer(invite.campaign).data
            })
        return Response(
            {'detail': 'Could not accept invite'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['post'])
    def decline(self, request, pk=None):
        """Decline an invite."""
        invite = self.get_object()

        if invite.invited_user != request.user.profile:
            return Response(
                {'detail': 'This invite is not for you'},
                status=status.HTTP_403_FORBIDDEN
            )

        if invite.decline():
            return Response({'detail': 'Invite declined'})
        return Response(
            {'detail': 'Could not decline invite'},
            status=status.HTTP_400_BAD_REQUEST
        )


# Direct invite creation (from campaign context)
def create_campaign_invite(request, campaign_pk):
    """Create an invite for a specific campaign."""
    campaign = get_object_or_404(Campaign, pk=campaign_pk)

    if campaign.gm != request.user.profile:
        return Response(
            {'detail': 'Only the GM can send invites'},
            status=status.HTTP_403_FORBIDDEN
        )

    serializer = CampaignInviteCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    invited_user = serializer.validated_data['invited_user_uuid']

    # Check if already invited or member
    if CampaignMembership.objects.filter(
        campaign=campaign,
        user=invited_user,
        status='active'
    ).exists():
        return Response(
            {'detail': 'User is already a member'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if CampaignInvite.objects.filter(
        campaign=campaign,
        invited_user=invited_user,
        status='pending'
    ).exists():
        return Response(
            {'detail': 'User already has a pending invite'},
            status=status.HTTP_400_BAD_REQUEST
        )

    invite = CampaignInvite.objects.create(
        campaign=campaign,
        invited_by=request.user.profile,
        invited_user=invited_user,
        role=serializer.validated_data.get('role', 'player'),
        message=serializer.validated_data.get('message', '')
    )

    return Response(
        CampaignInviteSerializer(invite).data,
        status=status.HTTP_201_CREATED
    )


# =============================================================================
# Campaign Custom Items
# =============================================================================

class CampaignItemViewSet(viewsets.ViewSet):
    """
    CRUD for campaign-scoped custom items (Weapons, Armor, Artifacts, Items).
    Uses existing compendium models with campaign FK.
    """
    permission_classes = [permissions.IsAuthenticated]

    ALLOWED_TYPES = {
        'weapon': 'compendium.Weapon',
        'armor': 'compendium.Armor',
        'artifact': 'compendium.Artifact',
        'item': 'compendium.Item',
    }

    def _get_campaign_and_check_membership(self, request, campaign_pk):
        """Get campaign and verify user is a member."""
        campaign = get_object_or_404(Campaign, pk=campaign_pk)
        user_profile = request.user.profile

        is_member = (
            campaign.gm == user_profile or
            CampaignMembership.objects.filter(
                campaign=campaign,
                user=user_profile,
                status='active'
            ).exists()
        )

        if not is_member:
            return None, None, Response(
                {'detail': 'You are not a member of this campaign'},
                status=status.HTTP_403_FORBIDDEN
            )

        is_gm = campaign.gm == user_profile
        return campaign, is_gm, None

    def _get_model(self, item_type):
        """Get the Django model class for the item type."""
        from compendium.models import Weapon, Armor, Artifact, Item
        model_map = {
            'weapon': Weapon,
            'armor': Armor,
            'artifact': Artifact,
            'item': Item,
        }
        return model_map.get(item_type)

    def list(self, request, campaign_pk=None):
        """List all custom items for this campaign."""
        campaign, is_gm, error = self._get_campaign_and_check_membership(request, campaign_pk)
        if error:
            return error

        from compendium.models import Weapon, Armor, Artifact, Item

        items = []
        for model, type_name in [(Weapon, 'weapon'), (Armor, 'armor'), (Artifact, 'artifact'), (Item, 'item')]:
            qs = model.objects.filter(campaign=campaign, is_official=False)
            if type_name == 'weapon':
                qs = qs.prefetch_related('dice', 'scaling', 'spell_scaling', 'requirements', 'bonuses')
            elif type_name == 'armor':
                qs = qs.prefetch_related('bonuses').select_related('requirements')
            elif type_name == 'artifact':
                qs = qs.prefetch_related('bonuses', 'upgrades')
            elif type_name == 'item':
                qs = qs.prefetch_related('bonuses')

            for obj in qs:
                item_data = {
                    'id': obj.id,
                    'type': type_name,
                    'name': obj.name,
                    'description': obj.description if hasattr(obj, 'description') else '',
                    'created_by': obj.created_by.username if obj.created_by else None,
                    'created_at': obj.created_at.isoformat() if obj.created_at else None,
                }

                # Add type-specific fields for edit support
                if type_name == 'weapon':
                    item_data.update({
                        'weapon_type': obj.weapon_type,
                        'second_type': obj.second_type,
                        'ap': obj.ap,
                        'durability': obj.durability,
                        'infusion': obj.infusion,
                        'is_trick': obj.is_trick,
                        'is_twin': obj.is_twin,
                        'skill_primary': obj.skill_primary_id,
                        'skill_secondary': obj.skill_secondary_id,
                        'second_ap': obj.second_ap,
                        'second_infusion': obj.second_infusion,
                        'second_skill_primary': obj.second_skill_primary_id if hasattr(obj, 'second_skill_primary_id') else None,
                        'second_skill_secondary': obj.second_skill_secondary_id if hasattr(obj, 'second_skill_secondary_id') else None,
                        'dice': [{'type': d.type, 'count': d.count, 'value': d.value, 'form': d.form} for d in obj.dice.all()],
                        'scaling': [{'type': s.type, 'stat': s.stat, 'value': s.value, 'form': s.form} for s in obj.scaling.all()],
                        'spell_scaling': [{'stat': s.stat, 'requirement': s.requirement, 'value': s.value, 'form': s.form} for s in obj.spell_scaling.all()],
                        'requirements': None,
                        'secondary_requirements': None,
                        'bonuses': [{'type': b.type, 'value': b.value} for b in obj.bonuses.all()],
                    })
                    # Primary form requirements
                    primary_reqs = obj.requirements.filter(form='primary').first()
                    if primary_reqs:
                        item_data['requirements'] = {'str': primary_reqs.str, 'dex': primary_reqs.dex, 'int': primary_reqs.int, 'fai': primary_reqs.fai}
                    # Secondary form requirements
                    secondary_reqs = obj.requirements.filter(form='secondary').first()
                    if secondary_reqs:
                        item_data['secondary_requirements'] = {'str': secondary_reqs.str, 'dex': secondary_reqs.dex, 'int': secondary_reqs.int, 'fai': secondary_reqs.fai}
                elif type_name == 'armor':
                    item_data.update({
                        'armor_type': obj.armor_type,
                        'durability': obj.durability,
                        'requirements': None,
                        'bonuses': [{'type': b.type, 'value': b.value, 'is_innate': b.is_innate} for b in obj.bonuses.all()],
                    })
                    try:
                        reqs = obj.requirements
                        item_data['requirements'] = {'str': reqs.str, 'dex': reqs.dex, 'int': reqs.int, 'fai': reqs.fai}
                    except Exception:
                        pass
                elif type_name == 'artifact':
                    item_data.update({
                        'bonuses': [{'type': b.type, 'value': b.value} for b in obj.bonuses.all()],
                        'upgrades': [{
                            'name': u.name, 'description': u.description,
                            'unlock_requirements': u.unlock_requirements,
                            'visible': u.visible, 'requirements_visible': u.requirements_visible,
                        } for u in obj.upgrades.all()],
                    })
                elif type_name == 'item':
                    item_data.update({
                        'item_type': obj.item_type,
                        'range': obj.range,
                        'duration': obj.duration,
                        'bonuses': [{'type': b.type, 'value': b.value} for b in obj.bonuses.all()],
                    })

                items.append(item_data)

        return Response(items)

    def create(self, request, campaign_pk=None):
        """Create a custom item for this campaign."""
        campaign, is_gm, error = self._get_campaign_and_check_membership(request, campaign_pk)
        if error:
            return error

        item_type = request.data.get('type')
        if item_type not in self.ALLOWED_TYPES:
            return Response(
                {'detail': f'Invalid item type. Allowed: {", ".join(self.ALLOWED_TYPES.keys())}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        Model = self._get_model(item_type)
        name = request.data.get('name', '').strip()
        description = request.data.get('description', '').strip()

        if not name:
            return Response({'detail': 'Name is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Build create kwargs from request data
        create_kwargs = {
            'name': name,
            'description': description,
            'campaign': campaign,
            'created_by': request.user,
            'is_official': False,
        }

        # Type-specific fields
        if item_type == 'weapon':
            create_kwargs['weapon_type'] = request.data.get('weapon_type', 'FIST')
            second_type = request.data.get('second_type')
            if second_type:
                create_kwargs['second_type'] = second_type
            create_kwargs['ap'] = request.data.get('ap', 3)
            create_kwargs['durability'] = request.data.get('durability', 10)
            create_kwargs['is_trick'] = request.data.get('is_trick', False)
            create_kwargs['is_twin'] = request.data.get('is_twin', False)
            infusion = request.data.get('infusion')
            if infusion:
                create_kwargs['infusion'] = infusion
            # Skill FKs (optional, stored as IDs referencing WeaponSkill)
            skill_primary = request.data.get('skill_primary')
            if skill_primary:
                create_kwargs['skill_primary_id'] = skill_primary
            skill_secondary = request.data.get('skill_secondary')
            if skill_secondary:
                create_kwargs['skill_secondary_id'] = skill_secondary
            # Secondary form fields (trick weapons)
            if request.data.get('is_trick'):
                second_ap = request.data.get('second_ap')
                if second_ap is not None:
                    create_kwargs['second_ap'] = second_ap
                second_infusion = request.data.get('second_infusion')
                if second_infusion:
                    create_kwargs['second_infusion'] = second_infusion
                second_skill_primary = request.data.get('second_skill_primary')
                if second_skill_primary:
                    create_kwargs['second_skill_primary_id'] = second_skill_primary
                second_skill_secondary = request.data.get('second_skill_secondary')
                if second_skill_secondary:
                    create_kwargs['second_skill_secondary_id'] = second_skill_secondary
        elif item_type == 'armor':
            create_kwargs['armor_type'] = request.data.get('armor_type', 'MEDIUM')
            create_kwargs['durability'] = request.data.get('durability', 10)
        elif item_type == 'item':
            create_kwargs['item_type'] = request.data.get('item_type', 'MISC')
            create_kwargs['range'] = request.data.get('range', '')
            create_kwargs['duration'] = request.data.get('duration', '')

        try:
            obj = Model.objects.create(**create_kwargs)

            # Create related models (scaling, dice, requirements, bonuses)
            self._create_related_models(item_type, obj, request.data)

        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'id': obj.id,
            'type': item_type,
            'name': obj.name,
            'description': obj.description if hasattr(obj, 'description') else '',
            'campaign_id': str(campaign.id),
        }, status=status.HTTP_201_CREATED)

    def _clear_related_models(self, item_type, obj):
        """Clear all related models before recreating (for updates)."""
        if item_type == 'weapon':
            obj.dice.all().delete()
            obj.scaling.all().delete()
            obj.spell_scaling.all().delete()
            obj.requirements.all().delete()
            obj.bonuses.all().delete()
        elif item_type == 'armor':
            try:
                obj.requirements.delete()
            except Exception:
                pass
            obj.bonuses.all().delete()
        elif item_type == 'artifact':
            obj.bonuses.all().delete()
            obj.upgrades.all().delete()
        elif item_type == 'item':
            obj.bonuses.all().delete()

    def _create_related_models(self, item_type, obj, data):
        """Create related models (dice, scaling, requirements, bonuses, upgrades)."""
        from compendium.models import (
            WeaponDice, WeaponScaling, SpellScaling, WeaponRequirements,
            WeaponBonuses, ArmorRequirements, ArmorBonuses,
            ArtifactBonuses, ArtifactUpgrade, ItemBonuses
        )

        # Requirements (weapon + armor)
        requirements = data.get('requirements')
        if requirements and any(v != 0 for v in [
            requirements.get('str', 0), requirements.get('dex', 0),
            requirements.get('int', 0), requirements.get('fai', 0)
        ]):
            if item_type == 'weapon':
                WeaponRequirements.objects.create(
                    weapon=obj,
                    form='primary',
                    str=requirements.get('str', 0),
                    dex=requirements.get('dex', 0),
                    int=requirements.get('int', 0),
                    fai=requirements.get('fai', 0),
                )
            elif item_type == 'armor':
                ArmorRequirements.objects.create(
                    armor=obj,
                    str=requirements.get('str', 0),
                    dex=requirements.get('dex', 0),
                    int=requirements.get('int', 0),
                    fai=requirements.get('fai', 0),
                )

        # Secondary requirements (trick weapons only)
        secondary_requirements = data.get('secondary_requirements')
        if item_type == 'weapon' and secondary_requirements and any(v != 0 for v in [
            secondary_requirements.get('str', 0), secondary_requirements.get('dex', 0),
            secondary_requirements.get('int', 0), secondary_requirements.get('fai', 0)
        ]):
            WeaponRequirements.objects.create(
                weapon=obj,
                form='secondary',
                str=secondary_requirements.get('str', 0),
                dex=secondary_requirements.get('dex', 0),
                int=secondary_requirements.get('int', 0),
                fai=secondary_requirements.get('fai', 0),
            )

        # Dice (weapon only)
        if item_type == 'weapon':
            for die in data.get('dice', []):
                WeaponDice.objects.create(
                    weapon=obj,
                    type=die.get('type', 'PHYSICAL'),
                    count=die.get('count', 1),
                    value=die.get('value', 6),
                    form=die.get('form', 'primary'),
                )

        # Scaling (weapon only)
        if item_type == 'weapon':
            for scale in data.get('scaling', []):
                WeaponScaling.objects.create(
                    weapon=obj,
                    type=scale.get('type', 'PHYSICAL'),
                    stat=scale.get('stat', 'STR'),
                    value=scale.get('value', 'D'),
                    form=scale.get('form', 'primary'),
                )

        # Spell Scaling (weapon only - for catalyst weapons)
        if item_type == 'weapon':
            for ss in data.get('spell_scaling', []):
                SpellScaling.objects.create(
                    weapon=obj,
                    stat=ss.get('stat', 'INT'),
                    requirement=ss.get('requirement', 0),
                    value=ss.get('value', 'D'),
                    form=ss.get('form', 'primary'),
                )

        # Bonuses (all types)
        BonusModel = {
            'weapon': WeaponBonuses,
            'armor': ArmorBonuses,
            'artifact': ArtifactBonuses,
            'item': ItemBonuses,
        }.get(item_type)

        if BonusModel:
            fk_field = item_type  # weapon, armor, artifact, item
            for bonus in data.get('bonuses', []):
                create_args = {
                    fk_field: obj,
                    'type': bonus.get('type', 'MAX_HP'),
                    'value': bonus.get('value', 0),
                }
                if item_type == 'armor' and 'is_innate' in bonus:
                    create_args['is_innate'] = bonus['is_innate']
                BonusModel.objects.create(**create_args)

        # Upgrades (artifact only)
        if item_type == 'artifact':
            for upgrade in data.get('upgrades', []):
                ArtifactUpgrade.objects.create(
                    artifact=obj,
                    name=upgrade.get('name', ''),
                    description=upgrade.get('description', ''),
                    unlock_requirements=upgrade.get('unlock_requirements', ''),
                    visible=upgrade.get('visible', False),
                    requirements_visible=upgrade.get('requirements_visible', False),
                )

    def partial_update(self, request, campaign_pk=None, pk=None):
        """Edit a custom item (creator or GM only)."""
        campaign, is_gm, error = self._get_campaign_and_check_membership(request, campaign_pk)
        if error:
            return error

        item_type = request.data.get('type')
        Model = self._get_model(item_type)
        if not Model:
            return Response({'detail': 'Invalid item type'}, status=status.HTTP_400_BAD_REQUEST)

        obj = get_object_or_404(Model, pk=pk, campaign=campaign, is_official=False)

        # Only creator or GM can edit
        if obj.created_by != request.user and not is_gm:
            return Response({'detail': 'Only the creator or GM can edit this item'}, status=status.HTTP_403_FORBIDDEN)

        # Update core fields
        if 'name' in request.data:
            obj.name = request.data['name']
        if 'description' in request.data:
            obj.description = request.data['description']

        # Type-specific core field updates
        if item_type == 'weapon':
            for field in ['weapon_type', 'second_type', 'ap', 'durability', 'infusion',
                          'is_trick', 'is_twin', 'second_ap', 'second_infusion']:
                if field in request.data:
                    setattr(obj, field, request.data[field])
            # Skill FK fields (use _id suffix for Django FK assignment)
            for field, fk_field in [('skill_primary', 'skill_primary_id'),
                                     ('skill_secondary', 'skill_secondary_id'),
                                     ('second_skill_primary', 'second_skill_primary_id'),
                                     ('second_skill_secondary', 'second_skill_secondary_id')]:
                if field in request.data:
                    setattr(obj, fk_field, request.data[field])
        elif item_type == 'armor':
            for field in ['armor_type', 'durability']:
                if field in request.data:
                    setattr(obj, field, request.data[field])
        elif item_type == 'item':
            for field in ['item_type', 'range', 'duration']:
                if field in request.data:
                    setattr(obj, field, request.data[field])

        obj.updated_by = request.user
        obj.save()

        # Clear and recreate related models if provided
        if any(k in request.data for k in ['dice', 'scaling', 'spell_scaling', 'requirements', 'bonuses', 'upgrades']):
            self._clear_related_models(item_type, obj)
            self._create_related_models(item_type, obj, request.data)

        return Response({
            'id': obj.id,
            'type': item_type,
            'name': obj.name,
            'description': obj.description if hasattr(obj, 'description') else '',
        })

    def destroy(self, request, campaign_pk=None, pk=None):
        """Delete a custom item (creator or GM only)."""
        campaign, is_gm, error = self._get_campaign_and_check_membership(request, campaign_pk)
        if error:
            return error

        # Try each model type (type is unknown for delete by ID)
        from compendium.models import Weapon, Armor, Artifact, Item
        obj = None
        for Model in [Weapon, Armor, Artifact, Item]:
            try:
                obj = Model.objects.get(pk=pk, campaign=campaign, is_official=False)
                break
            except Model.DoesNotExist:
                continue

        if not obj:
            return Response({'detail': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)

        if obj.created_by != request.user and not is_gm:
            return Response({'detail': 'Only the creator or GM can delete this item'}, status=status.HTTP_403_FORBIDDEN)

        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
