from datetime import date

from django.core.exceptions import ValidationError


def validate_tasting_date_not_future(value):
    if value > date.today():
        raise ValidationError("A data da degustação não pode estar no futuro.")


def validate_vintage_year(value):
    if value is None:
        return
    current_year = date.today().year
    if not (1800 <= value <= current_year):
        raise ValidationError(f"A safra deve estar entre 1800 e {current_year}.")
