from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed


class ExpiringTokenAuthentication(TokenAuthentication):
    """DRF token auth with a sliding refresh window and a hard creation cap.

    A token is rejected when either:
      * now > token.created + TOKEN_HARD_CAP_DAYS (the absolute ceiling), or
      * now > profile.token_last_used + TOKEN_SLIDING_WINDOW_HOURS (inactive).

    Each successful authentication bumps ``profile.token_last_used`` so active
    users keep their session alive until they hit the hard cap. Expired tokens
    are deleted so the next login starts fresh.
    """

    def authenticate_credentials(self, key):
        user, token = super().authenticate_credentials(key)

        app_hard_cap_days = getattr(settings, 'TOKEN_HARD_CAP_DAYS', 6)
        foundry_hard_cap_hours = getattr(settings, 'TOKEN_FOUNDRY_HARD_CAP_HOURS', 12)
        sliding_hours = getattr(settings, 'TOKEN_SLIDING_WINDOW_HOURS', 24)
        now = timezone.now()

        profile = getattr(user, 'profile', None)
        last_foundry_login = getattr(profile, 'last_foundry_login', None) if profile else None
        last_login = getattr(profile, 'last_login', None) if profile else None

        is_foundry_token = (
            last_foundry_login is not None
            and (last_login is None or last_foundry_login > last_login)
        )

        if is_foundry_token:
            if last_foundry_login < now - timedelta(hours=foundry_hard_cap_hours):
                token.delete()
                raise AuthenticationFailed('Foundry token expired (hard cap reached).')
        else:
            if token.created < now - timedelta(days=app_hard_cap_days):
                token.delete()
                raise AuthenticationFailed('Token expired (hard cap reached).')

        last_used = getattr(profile, 'token_last_used', None) if profile else None
        if last_used and last_used < now - timedelta(hours=sliding_hours):
            token.delete()
            raise AuthenticationFailed('Token expired (inactive).')

        if profile is not None:
            profile.token_last_used = now
            profile.save(update_fields=['token_last_used'])

        return (user, token)
