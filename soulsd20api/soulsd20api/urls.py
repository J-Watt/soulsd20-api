"""
URL configuration for soulsd20api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.http import HttpResponse

# Customize admin site headers
admin.site.site_header = 'SD20 Administration'
admin.site.site_title = 'SD20 Admin'
admin.site.index_title = 'Welcome to SD20 Administration'


def setup_production_view(request):
    """One-time setup endpoint. Visit once then remove."""
    from django.core.management import call_command
    from django.contrib.auth.models import User
    from io import StringIO
    output = StringIO()

    # Load complete compendium from full dump
    fixtures = [
        'compendium/fixtures/full_compendium_dump.json',
    ]

    from compendium.models import Weapon, Spell
    # Load if spells are missing (partial load from before)
    if Spell.objects.count() == 0:
        for f in fixtures:
            try:
                call_command('loaddata', f, verbosity=0)
                output.write(f'Loaded {f}\n')
            except Exception as e:
                output.write(f'FAILED {f}: {e}\n')
    else:
        output.write(f'Compendium already has {Weapon.objects.count()} weapons, skipping fixtures.\n')

    # Create superuser
    if not User.objects.filter(username='bell').exists():
        user = User.objects.create_superuser('bell', 'belminsestic55@gmail.com', 'Kjhhjkkk1!')
        output.write('Superuser "bell" created.\n')
        from accounts.models import UserProfile
        if not hasattr(user, 'profile'):
            UserProfile.objects.create(
                user=user, user_type='permanent', subscription_status='active_patron',
                is_admin=True, max_characters=50, max_campaigns_as_gm=20,
            )
            output.write('UserProfile created.\n')
    else:
        output.write('Superuser "bell" already exists.\n')

    return HttpResponse(f'<pre>{output.getvalue()}</pre>')


urlpatterns = [
    # One-time setup (remove after use)
    path('setup-production-xyz/', setup_production_view),

    # Admin
    path('admin/', admin.site.urls),

    # Browsable API authentication
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    # Compendium API (existing read-only endpoints)
    # Endpoints: /weapons/, /armor/, /spells/, /spirits/, /lineages/, etc.
    path('', include('compendium.urls')),

    # New API endpoints under /api/
    # Authentication: /api/auth/login/, /api/auth/logout/, /api/auth/me/
    path('api/', include('accounts.urls')),

    # Characters: /api/characters/
    path('api/', include('characters.urls')),

    # Campaigns: /api/campaigns/
    path('api/campaigns/', include('campaigns.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
