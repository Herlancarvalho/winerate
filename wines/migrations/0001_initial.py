import decimal

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import wines.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Wine",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200, verbose_name="nome")),
                ("winery", models.CharField(blank=True, max_length=200, verbose_name="vinícola")),
                ("vintage", models.PositiveSmallIntegerField(blank=True, null=True, validators=[wines.validators.validate_vintage_year], verbose_name="safra")),
                ("country", models.CharField(blank=True, max_length=100, verbose_name="país")),
                ("region", models.CharField(blank=True, max_length=150, verbose_name="região")),
                ("grape", models.CharField(blank=True, max_length=150, verbose_name="uva")),
                ("price", models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, validators=[django.core.validators.MinValueValidator(decimal.Decimal("0"))], verbose_name="preço")),
                ("location", models.CharField(blank=True, max_length=200, verbose_name="local de consumo/compra")),
                ("rating", models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)], verbose_name="nota")),
                ("comment", models.TextField(blank=True, verbose_name="comentário")),
                ("tasting_date", models.DateField(validators=[wines.validators.validate_tasting_date_not_future], verbose_name="data da degustação")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="criado em")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="atualizado em")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="wines", to=settings.AUTH_USER_MODEL, verbose_name="usuário")),
            ],
            options={
                "ordering": ["-tasting_date", "-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="wine",
            index=models.Index(fields=["user", "-tasting_date"], name="wine_user_tasting_idx"),
        ),
        migrations.AddIndex(
            model_name="wine",
            index=models.Index(fields=["user", "rating"], name="wine_user_rating_idx"),
        ),
        migrations.AddIndex(
            model_name="wine",
            index=models.Index(fields=["user", "country"], name="wine_user_country_idx"),
        ),
        migrations.AddIndex(
            model_name="wine",
            index=models.Index(fields=["user", "grape"], name="wine_user_grape_idx"),
        ),
        migrations.AddConstraint(
            model_name="wine",
            constraint=models.CheckConstraint(
                condition=models.Q(("rating__gte", 1), ("rating__lte", 5)),
                name="wine_rating_between_1_and_5",
            ),
        ),
    ]
