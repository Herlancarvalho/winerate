from rest_framework.permissions import BasePermission

from .models import Wine


class IsOwner(BasePermission):
    """Permissão em nível de objeto: só o dono lê, edita ou exclui."""

    def has_object_permission(self, request, view, obj):
        return obj.user_id == request.user.id


class OwnedQuerySetMixin:
    """
    Restringe o queryset ao usuário logado. Um vinho alheio devolve 404,
    sem revelar que o ID existe.
    """

    def get_queryset(self):
        return Wine.objects.for_user(self.request.user)
