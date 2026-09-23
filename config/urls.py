from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path

urlpatterns = [
    path("healthz", lambda request: HttpResponse("ok"), name="healthz"),
    path("admin/", admin.site.urls),
    path("api/", include("accounts.urls")),
    path("api/", include("wines.urls")),
    path("", include("web.urls")),
]
