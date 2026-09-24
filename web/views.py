import json
from pathlib import Path

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import redirect
from django.templatetags.static import static
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET
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


@require_GET
def manifest(request):
    """Manifesto do aplicativo instalável (PWA)."""
    data = {
        "name": "Wine Rate",
        "short_name": "Wine Rate",
        "description": "O diário das suas degustações de vinho.",
        "lang": "pt-BR",
        "start_url": "/",
        "scope": "/",
        "display": "standalone",
        "orientation": "portrait",
        "background_color": "#5c1226",
        "theme_color": "#3b0a1a",
        "icons": [
            {"src": static("web/icons/icon-192.png"), "sizes": "192x192", "type": "image/png", "purpose": "any maskable"},
            {"src": static("web/icons/icon-512.png"), "sizes": "512x512", "type": "image/png", "purpose": "any maskable"},
        ],
    }
    return HttpResponse(json.dumps(data), content_type="application/manifest+json")


@require_GET
@never_cache
def service_worker(request):
    """O service worker precisa ser servido da raiz (/sw.js) para controlar o site todo."""
    code = (Path(__file__).parent / "sw.js").read_text(encoding="utf-8")
    return HttpResponse(code, content_type="application/javascript")
