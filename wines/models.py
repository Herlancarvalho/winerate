from decimal import Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q

from .validators import validate_tasting_date_not_future, validate_vintage_year


class WineQuerySet(models.QuerySet):
    def for_user(self, user):
        """Único ponto de acesso a vinhos: sempre restringe ao dono."""
        if not user or not user.is_authenticated:
            return self.none()
        return self.filter(user=user)


class Wine(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wines",
        verbose_name="usuário",
    )
    name = models.CharField("nome", max_length=200)
    winery = models.CharField("vinícola", max_length=200, blank=True)
    vintage = models.PositiveSmallIntegerField(
        "safra", null=True, blank=True, validators=[validate_vintage_year]
    )
    country = models.CharField("país", max_length=100, blank=True)
    region = models.CharField("região", max_length=150, blank=True)
    grape = models.CharField("uva", max_length=150, blank=True)
    price = models.DecimalField(
        "preço",
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0"))],
    )
    location = models.CharField("local de consumo/compra", max_length=200, blank=True)
    rating = models.PositiveSmallIntegerField(
        "nota", validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField("comentário", blank=True)
    tasting_date = models.DateField(
        "data da degustação", validators=[validate_tasting_date_not_future]
    )
    created_at = models.DateTimeField("criado em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)

    objects = WineQuerySet.as_manager()

    class Meta:
        ordering = ["-tasting_date", "-created_at"]
        indexes = [
            models.Index(fields=["user", "-tasting_date"], name="wine_user_tasting_idx"),
            models.Index(fields=["user", "rating"], name="wine_user_rating_idx"),
            models.Index(fields=["user", "country"], name="wine_user_country_idx"),
            models.Index(fields=["user", "grape"], name="wine_user_grape_idx"),
        ]
        constraints = [
            # Garantia final no banco, mesmo que a validação da aplicação seja contornada
            models.CheckConstraint(
                condition=Q(rating__gte=1) & Q(rating__lte=5),
                name="wine_rating_between_1_and_5",
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.vintage or 'NV'})"
