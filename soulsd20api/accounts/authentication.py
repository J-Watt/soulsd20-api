from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed

from .models import AuthToken


class ExpiringTokenAuthentication(TokenAuthentication):
    """Token auth backed by accounts.AuthToken (one row per active context per
    user). The token's source ('app' or 'foundry') drives the expiry cap so
    Foundry-issued tokens get the shorter window without leaking into App
    sessions."""

    def get_model(self):
        return AuthToken

    def authenticate_credentials(self, key):
        user, token = super().authenticate_credentials(key)

        now = timezone.now()
        sliding_hours = getattr(settings, 'TOKEN_SLIDING_WINDOW_HOURS', 24)

        if token.source == AuthToken.SOURCE_FOUNDRY:
            cap_hours = getattr(settings, 'TOKEN_FOUNDRY_HARD_CAP_HOURS', 12)
            if token.created < now - timedelta(hours=cap_hours):
                token.delete()
                raise AuthenticationFailed('Foundry token expired (hard cap reached).')
        else:
            cap_days = getattr(settings, 'TOKEN_HARD_CAP_DAYS', 6)
            if token.created < now - timedelta(days=cap_days):
                token.delete()
                raise AuthenticationFailed('Token expired (hard cap reached).')

        if token.last_used and token.last_used < now - timedelta(hours=sliding_hours):
            token.delete()
            raise AuthenticationFailed('Token expired (inactive).')

        token.last_used = now
        token.save(update_fields=['last_used'])

        return (user, token)
