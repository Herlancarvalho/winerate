from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import DashboardView, WineViewSet

router = SimpleRouter(trailing_slash=False)
router.register("wines", WineViewSet, basename="wine")

urlpatterns = router.urls + [
    path("dashboard", DashboardView.as_view(), name="api-dashboard"),
]
