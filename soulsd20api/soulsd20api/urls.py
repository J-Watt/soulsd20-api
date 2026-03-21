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

# Customize admin site headers
admin.site.site_header = 'SD20 Administration'
admin.site.site_title = 'SD20 Admin'
admin.site.index_title = 'Welcome to SD20 Administration'


urlpatterns = [
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
