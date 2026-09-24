from django.contrib.auth.views import LogoutView
from django.urls import path

from django.views.generic import TemplateView

from .views import PrivatePage, PublicAuthPage, manifest, service_worker

urlpatterns = [
    path("", PrivatePage.as_view(template_name="web/dashboard.html"), name="dashboard"),
    path("wines/", PrivatePage.as_view(template_name="web/wine_list.html"), name="wine-list"),
    path("wines/new/", PrivatePage.as_view(template_name="web/wine_form.html"), name="wine-new"),
    path("wines/<int:pk>/edit/", PrivatePage.as_view(template_name="web/wine_form.html"), name="wine-edit"),
    path("login/", PublicAuthPage.as_view(template_name="web/login.html"), name="login"),
    path("register/", PublicAuthPage.as_view(template_name="web/register.html"), name="register"),
    path("logout/", LogoutView.as_view(), name="logout"),  # Django 5: apenas POST
    # Aplicativo instalável (PWA)
    path("manifest.webmanifest", manifest, name="manifest"),
    path("sw.js", service_worker, name="service-worker"),
    path("offline/", TemplateView.as_view(template_name="web/offline.html"), name="offline"),
]
