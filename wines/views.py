from django.db.models import Avg, Count
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import WineFilter
from .models import Wine
from .permissions import IsOwner, OwnedQuerySetMixin
from .serializers import LabelImageSerializer, WineSerializer
from .services.label_vision import LabelVisionError, extract_label_data


class WineViewSet(OwnedQuerySetMixin, viewsets.ModelViewSet):
    """..."""

    serializer_class = WineSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    throttle_scope = None          # <- adicione esta linha
    filterset_class = WineFilter
    ordering_fields = ["tasting_date", "rating", "created_at", "name"]
    ordering = ["-tasting_date", "-created_at"]
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(
        detail=False,
        methods=["post"],
        url_path="identify-label",
        parser_classes=[MultiPartParser],
        throttle_scope="identify_label",
    )
    def identify_label(self, request):
        """Recebe a foto do rótulo e SOMENTE devolve os campos extraídos."""
        serializer = LabelImageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        image = serializer.validated_data["image"]
        try:
            data = extract_label_data(image.read(), image.content_type)
        except LabelVisionError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)
        # Nada é gravado: nem o registro, nem a imagem.
        return Response({"data": data, "review_required": True})


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Wine.objects.for_user(request.user)

        totals = qs.aggregate(total=Count("id"), avg=Avg("rating"))
        best = qs.order_by("-rating", "-tasting_date", "-created_at").first()
        last = qs.order_by("-created_at").first()

        def count_by(field):
            rows = (
                qs.exclude(**{field: ""})
                .values(field)
                .annotate(count=Count("id"))
                .order_by("-count", field)[:10]
            )
            return [{"label": r[field], "count": r["count"]} for r in rows]

        by_rating = {r["rating"]: r["count"] for r in qs.order_by().values("rating").annotate(count=Count("id"))}

        return Response({
            "total_wines": totals["total"],
            "average_rating": round(totals["avg"], 2) if totals["avg"] is not None else None,
            "best_wine": WineSerializer(best).data if best else None,
            "last_wine": WineSerializer(last).data if last else None,
            "by_country": count_by("country"),
            "by_grape": count_by("grape"),
            "by_rating": [{"rating": n, "count": by_rating.get(n, 0)} for n in range(5, 0, -1)],
        })
