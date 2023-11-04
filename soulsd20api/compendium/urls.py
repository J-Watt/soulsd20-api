from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'usageFormula', views.UsageFormulaViewSet)
router.register(r'weaponProfFeat', views.WeaponProfFeatViewSet)
router.register(r'destinyFeat', views.DestinyFeatViewSet)
router.register(r'weaponSkill', views.WeaponSkillViewSet)
router.register(r'item', views.ItemViewSet)
router.register(r'ring', views.RingViewSet)
router.register(r'artifact', views.ArtifactViewSet)
router.register(r'armor', views.ArmorViewSet)
router.register(r'weapon', views.WeaponViewSet)

# The API URLs are now determined automatically by the router.
# Additionally, we include the login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls))
]