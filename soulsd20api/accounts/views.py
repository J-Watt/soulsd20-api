from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.conf import settings
from django.shortcuts import redirect
from django.utils import timezone
import requests
import urllib.parse

from .models import UserProfile
from .serializers import UserProfileSerializer, MeSerializer


# =============================================================================
# Patreon OAuth Configuration
# =============================================================================
PATREON_OAUTH_AUTHORIZE_URL = 'https://www.patreon.com/oauth2/authorize'
PATREON_OAUTH_TOKEN_URL = 'https://www.patreon.com/api/oauth2/token'
PATREON_API_URL = 'https://www.patreon.com/api/oauth2/v2'

# Patreon tier IDs to tier names (configure these in settings or as needed)
PATREON_TIER_MAP = {
    # These will need to be updated with actual Patreon tier IDs
    # Format: 'patreon_tier_id': {'name': 'Tier Name', 'max_characters': 10, 'max_campaigns': 5}
}


class UserProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing user profiles.
    Read-only - profiles are created automatically via signals.
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'

    def get_queryset(self):
        """
        Non-admins can only see their own profile.
        Admins can see all profiles.
        """
        user = self.request.user
        if hasattr(user, 'profile') and user.profile.is_admin:
            return UserProfile.objects.all()
        return UserProfile.objects.filter(user=user)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    """
    Get current user's profile.
    GET /api/auth/me/
    """
    if not hasattr(request.user, 'profile'):
        return Response(
            {'error': 'User profile not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = MeSerializer(request.user.profile)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    Login with username/password (for permanent members).
    POST /api/auth/login/

    Request body:
    {
        "username": "string",
        "password": "string"
    }

    Returns:
    {
        "token": "string",
        "user": { ... }
    }
    """
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response(
            {'error': 'Username and password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(username=username, password=password)

    if not user:
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    if not user.is_active:
        return Response(
            {'error': 'Account is disabled'},
            status=status.HTTP_403_FORBIDDEN
        )

    # Check if user has a profile
    if not hasattr(user, 'profile'):
        UserProfile.objects.create(user=user)

    # Check if account is locked
    if user.profile.account_locked:
        return Response(
            {'error': 'Account is locked. Please renew your subscription.'},
            status=status.HTTP_403_FORBIDDEN
        )

    # Get or create auth token
    token, _ = Token.objects.get_or_create(user=user)

    # Update last login
    from django.utils import timezone
    user.profile.last_login = timezone.now()
    user.profile.save(update_fields=['last_login'])

    return Response({
        'token': token.key,
        'user': MeSerializer(user.profile).data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """
    Logout - invalidates the auth token.
    POST /api/auth/logout/
    """
    try:
        # Delete the user's token
        request.user.auth_token.delete()
        return Response({'message': 'Successfully logged out'})
    except Exception:
        return Response({'message': 'Logged out'})


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Register a new permanent member (admin-only in production).
    POST /api/auth/register/

    Request body:
    {
        "username": "string",
        "email": "string",
        "password": "string"
    }

    Note: In production, this should be restricted to admins only.
    Regular users should register via Patreon OAuth.
    """
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')

    if not username or not password:
        return Response(
            {'error': 'Username and password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Check if username already exists
    if User.objects.filter(username=username).exists():
        return Response(
            {'error': 'Username already exists'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Check if email already exists
    if email and User.objects.filter(email=email).exists():
        return Response(
            {'error': 'Email already exists'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Create user
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password
    )

    # Profile is created via signal, update it to permanent member
    user.profile.user_type = 'permanent'
    user.profile.save()

    # Create auth token
    token = Token.objects.create(user=user)

    return Response({
        'token': token.key,
        'user': MeSerializer(user.profile).data
    }, status=status.HTTP_201_CREATED)


# =============================================================================
# Patreon OAuth Flow
# =============================================================================

@api_view(['GET'])
@permission_classes([AllowAny])
def patreon_auth_url(request):
    """
    Get the Patreon OAuth authorization URL.
    GET /api/auth/patreon/

    Returns the URL to redirect the user to for Patreon authentication.
    """
    if not settings.PATREON_CLIENT_ID:
        return Response(
            {'error': 'Patreon integration not configured'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )

    # Build OAuth URL
    params = {
        'response_type': 'code',
        'client_id': settings.PATREON_CLIENT_ID,
        'redirect_uri': settings.PATREON_REDIRECT_URI,
        'scope': 'identity identity[email] campaigns.members',
        'state': request.query_params.get('state', ''),  # For CSRF protection
    }

    auth_url = f"{PATREON_OAUTH_AUTHORIZE_URL}?{urllib.parse.urlencode(params)}"

    return Response({'auth_url': auth_url})


@api_view(['POST'])
@permission_classes([AllowAny])
def patreon_callback(request):
    """
    Handle Patreon OAuth callback.
    POST /api/auth/patreon/callback/

    Request body:
    {
        "code": "string",  # OAuth authorization code
        "state": "string"  # Optional state for CSRF
    }

    Returns:
    {
        "token": "string",
        "user": { ... },
        "is_new_user": boolean
    }
    """
    code = request.data.get('code')

    if not code:
        return Response(
            {'error': 'Authorization code is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not settings.PATREON_CLIENT_ID or not settings.PATREON_CLIENT_SECRET:
        return Response(
            {'error': 'Patreon integration not configured'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )

    # Exchange code for access token
    token_response = requests.post(
        PATREON_OAUTH_TOKEN_URL,
        data={
            'code': code,
            'grant_type': 'authorization_code',
            'client_id': settings.PATREON_CLIENT_ID,
            'client_secret': settings.PATREON_CLIENT_SECRET,
            'redirect_uri': settings.PATREON_REDIRECT_URI,
        }
    )

    if not token_response.ok:
        return Response(
            {'error': 'Failed to exchange authorization code'},
            status=status.HTTP_400_BAD_REQUEST
        )

    token_data = token_response.json()
    access_token = token_data.get('access_token')
    refresh_token = token_data.get('refresh_token')

    if not access_token:
        return Response(
            {'error': 'No access token received'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Get user identity from Patreon
    identity_response = requests.get(
        f"{PATREON_API_URL}/identity",
        headers={'Authorization': f'Bearer {access_token}'},
        params={
            'include': 'memberships,memberships.campaign',
            'fields[user]': 'email,full_name,image_url',
            'fields[member]': 'patron_status,last_charge_date,last_charge_status,currently_entitled_amount_cents,pledge_relationship_start'
        }
    )

    if not identity_response.ok:
        return Response(
            {'error': 'Failed to get Patreon identity'},
            status=status.HTTP_400_BAD_REQUEST
        )

    identity_data = identity_response.json()
    patreon_user = identity_data.get('data', {})
    patreon_id = patreon_user.get('id')
    attributes = patreon_user.get('attributes', {})
    email = attributes.get('email')
    full_name = attributes.get('full_name', '')

    if not patreon_id:
        return Response(
            {'error': 'Invalid Patreon response'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Find or create user
    is_new_user = False
    try:
        profile = UserProfile.objects.get(patreon_id=patreon_id)
        user = profile.user
    except UserProfile.DoesNotExist:
        # Try to find by email
        try:
            user = User.objects.get(email=email)
            profile = user.profile
        except User.DoesNotExist:
            # Create new user
            is_new_user = True
            username = _generate_username(full_name, email)
            user = User.objects.create_user(
                username=username,
                email=email,
                password=None  # No password - Patreon auth only
            )
            profile = user.profile

    # Update profile with Patreon data
    profile.patreon_id = patreon_id
    profile.patreon_email = email
    profile.patreon_access_token = access_token
    profile.patreon_refresh_token = refresh_token

    # Parse membership data
    included = identity_data.get('included', [])
    membership = _find_campaign_membership(included, settings.PATREON_CAMPAIGN_ID)

    if membership:
        member_attrs = membership.get('attributes', {})
        profile.subscription_status = _map_patron_status(member_attrs.get('patron_status'))
        profile.last_charge_date = member_attrs.get('last_charge_date')
        profile.last_charge_status = member_attrs.get('last_charge_status')

        # Get tier info
        tier_cents = member_attrs.get('currently_entitled_amount_cents', 0)
        profile.subscription_tier = _get_tier_name(tier_cents)

        # Update limits based on tier
        limits = _get_tier_limits(tier_cents)
        profile.max_characters = limits.get('max_characters', 10)
        profile.max_campaigns_as_gm = limits.get('max_campaigns', 5)

        # Unlock account if active patron
        if profile.subscription_status == 'active_patron':
            profile.account_locked = False
    else:
        # Not a member of the Patreon campaign
        profile.subscription_status = 'never_patron'

    profile.save()

    # Get or create auth token
    token, _ = Token.objects.get_or_create(user=user)

    return Response({
        'token': token.key,
        'user': MeSerializer(profile).data,
        'is_new_user': is_new_user
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def refresh_patreon_status(request):
    """
    Refresh the user's Patreon membership status.
    POST /api/auth/patreon/refresh/

    Uses stored refresh token to get new access token and fetch current status.
    """
    profile = request.user.profile

    if not profile.patreon_refresh_token:
        return Response(
            {'error': 'No Patreon connection found'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Get new access token using refresh token
    token_response = requests.post(
        PATREON_OAUTH_TOKEN_URL,
        data={
            'grant_type': 'refresh_token',
            'refresh_token': profile.patreon_refresh_token,
            'client_id': settings.PATREON_CLIENT_ID,
            'client_secret': settings.PATREON_CLIENT_SECRET,
        }
    )

    if not token_response.ok:
        return Response(
            {'error': 'Failed to refresh Patreon token. Please reconnect.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    token_data = token_response.json()
    access_token = token_data.get('access_token')
    refresh_token = token_data.get('refresh_token')

    # Update stored tokens
    profile.patreon_access_token = access_token
    if refresh_token:
        profile.patreon_refresh_token = refresh_token

    # Get current membership status
    identity_response = requests.get(
        f"{PATREON_API_URL}/identity",
        headers={'Authorization': f'Bearer {access_token}'},
        params={
            'include': 'memberships,memberships.campaign',
            'fields[member]': 'patron_status,last_charge_date,last_charge_status,currently_entitled_amount_cents'
        }
    )

    if identity_response.ok:
        identity_data = identity_response.json()
        included = identity_data.get('included', [])
        membership = _find_campaign_membership(included, settings.PATREON_CAMPAIGN_ID)

        if membership:
            member_attrs = membership.get('attributes', {})
            profile.subscription_status = _map_patron_status(member_attrs.get('patron_status'))
            profile.last_charge_date = member_attrs.get('last_charge_date')
            profile.last_charge_status = member_attrs.get('last_charge_status')

            tier_cents = member_attrs.get('currently_entitled_amount_cents', 0)
            profile.subscription_tier = _get_tier_name(tier_cents)

            limits = _get_tier_limits(tier_cents)
            profile.max_characters = limits.get('max_characters', 10)
            profile.max_campaigns_as_gm = limits.get('max_campaigns', 5)

            if profile.subscription_status == 'active_patron':
                profile.account_locked = False
        else:
            profile.subscription_status = 'former_patron'

    profile.save()

    return Response({
        'user': MeSerializer(profile).data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def disconnect_patreon(request):
    """
    Disconnect Patreon from the account.
    POST /api/auth/patreon/disconnect/

    Clears Patreon tokens but preserves the account.
    """
    profile = request.user.profile

    profile.patreon_access_token = None
    profile.patreon_refresh_token = None
    # Keep patreon_id for tracking purposes
    profile.save()

    return Response({'message': 'Patreon disconnected'})


# =============================================================================
# Helper Functions
# =============================================================================

def _generate_username(full_name, email):
    """Generate a unique username from full name or email."""
    import re
    import random
    import string

    # Try full name first
    if full_name:
        base = re.sub(r'[^a-zA-Z0-9]', '', full_name.lower())[:15]
    elif email:
        base = email.split('@')[0][:15]
    else:
        base = 'user'

    # Ensure uniqueness
    username = base
    counter = 1
    while User.objects.filter(username=username).exists():
        suffix = ''.join(random.choices(string.digits, k=4))
        username = f"{base}{suffix}"
        counter += 1
        if counter > 10:
            username = f"user{''.join(random.choices(string.ascii_lowercase + string.digits, k=8))}"
            break

    return username


def _find_campaign_membership(included, campaign_id):
    """Find membership data for our specific campaign."""
    if not campaign_id:
        return None

    for item in included:
        if item.get('type') == 'member':
            relationships = item.get('relationships', {})
            campaign = relationships.get('campaign', {}).get('data', {})
            if campaign.get('id') == campaign_id:
                return item

    # If no specific campaign match, return first membership
    for item in included:
        if item.get('type') == 'member':
            return item

    return None


def _map_patron_status(status):
    """Map Patreon patron_status to our subscription_status."""
    status_map = {
        'active_patron': 'active_patron',
        'declined_patron': 'declined_patron',
        'former_patron': 'former_patron',
    }
    return status_map.get(status, 'never_patron')


def _get_tier_name(cents):
    """Get tier name based on pledge amount in cents."""
    if cents >= 2000:  # $20+
        return 'Champion'
    elif cents >= 1000:  # $10+
        return 'Hero'
    elif cents >= 500:  # $5+
        return 'Adventurer'
    elif cents > 0:
        return 'Supporter'
    return None


def _get_tier_limits(cents):
    """Get character/campaign limits based on tier."""
    if cents >= 2000:  # Champion
        return {'max_characters': 50, 'max_campaigns': 20}
    elif cents >= 1000:  # Hero
        return {'max_characters': 25, 'max_campaigns': 10}
    elif cents >= 500:  # Adventurer
        return {'max_characters': 15, 'max_campaigns': 7}
    elif cents > 0:  # Supporter
        return {'max_characters': 10, 'max_campaigns': 5}
    return {'max_characters': 5, 'max_campaigns': 2}  # Free tier
