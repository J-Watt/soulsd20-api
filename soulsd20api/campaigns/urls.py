"""
Campaign URL Configuration for SD20 API.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'', views.CampaignViewSet, basename='campaign')

# Nested routes for invites
invite_router = DefaultRouter()
invite_router.register(r'', views.CampaignInviteViewSet, basename='invite')

urlpatterns = [
    # User's received invites (must come BEFORE campaign router to avoid UUID lookup conflict)
    path('invites/', include(invite_router.urls)),

    # Campaign CRUD and actions
    path('', include(router.urls)),

    # Campaign-specific membership management
    path('<uuid:campaign_pk>/members/',
         views.CampaignMembershipViewSet.as_view({
             'get': 'list',
         }),
         name='campaign-members'),
    path('<uuid:campaign_pk>/members/<uuid:pk>/',
         views.CampaignMembershipViewSet.as_view({
             'get': 'retrieve',
             'delete': 'destroy',
         }),
         name='campaign-member-detail'),
    path('<uuid:campaign_pk>/members/<uuid:pk>/kick/',
         views.CampaignMembershipViewSet.as_view({
             'post': 'kick',
         }),
         name='campaign-member-kick'),
    path('<uuid:campaign_pk>/members/<uuid:pk>/change-role/',
         views.CampaignMembershipViewSet.as_view({
             'post': 'change_role',
         }),
         name='campaign-member-change-role'),

    # Campaign-specific invites
    path('<uuid:campaign_pk>/invite/',
         views.create_campaign_invite,
         name='campaign-invite-create'),

    # Campaign custom items
    path('<uuid:campaign_pk>/items/',
         views.CampaignItemViewSet.as_view({
             'get': 'list',
             'post': 'create',
         }),
         name='campaign-items'),
    path('<uuid:campaign_pk>/items/<int:pk>/',
         views.CampaignItemViewSet.as_view({
             'patch': 'partial_update',
             'delete': 'destroy',
         }),
         name='campaign-item-detail'),
]
