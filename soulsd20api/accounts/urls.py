from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'profiles', views.UserProfileViewSet, basename='userprofile')

urlpatterns = [
    # Auth endpoints
    path('auth/me/', views.me, name='auth-me'),
    path('auth/login/', views.login, name='auth-login'),
    path('auth/logout/', views.logout, name='auth-logout'),
    path('auth/register/', views.register, name='auth-register'),

    # Patreon OAuth endpoints
    path('auth/patreon/', views.patreon_auth_url, name='patreon-auth-url'),
    path('auth/patreon/callback/', views.patreon_callback, name='patreon-callback'),
    path('auth/patreon/refresh/', views.refresh_patreon_status, name='patreon-refresh'),
    path('auth/patreon/disconnect/', views.disconnect_patreon, name='patreon-disconnect'),

    # Profile endpoints
    path('', include(router.urls)),
]
