from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import TemplateView


@method_decorator(ensure_csrf_cookie, name="dispatch")
class PrivatePage(LoginRequiredMixin, TemplateView):
    """Páginas do app: exigem login e garantem o cookie CSRF para o fetch."""


@method_decorator(ensure_csrf_cookie, name="dispatch")
class PublicAuthPage(TemplateView):
    """Login e cadastro: quem já está logado vai direto ao dashboard."""

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("dashboard")
        return super().dispatch(request, *args, **kwargs)
