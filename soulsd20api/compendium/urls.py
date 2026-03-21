from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

# Router registration for compendium viewsets
router = DefaultRouter()
router.register(r'usageFormula', views.UsageFormulaViewSet)
router.register(r'weaponProfFeat', views.WeaponProfFeatViewSet)
router.register(r'destinyFeat', views.DestinyFeatViewSet)
router.register(r'weaponSkill', views.WeaponSkillViewSet)
router.register(r'spell', views.SpellViewSet)
router.register(r'spirit', views.SpiritViewSet)
router.register(r'item', views.ItemViewSet)
router.register(r'ring', views.RingViewSet)
router.register(r'artifact', views.ArtifactViewSet)
router.register(r'armor', views.ArmorViewSet)
router.register(r'weapon', views.WeaponViewSet)
router.register(r'backgrounds', views.BackgroundViewSet)
router.register(r'lineages', views.LineageViewSet)
router.register(r'bloodlines', views.BloodlineViewSet)

# The API URLs are now determined automatically by the router.
# API URLs determined automatically by the router
urlpatterns = [
    path('', include(router.urls))
]