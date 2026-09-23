import django_filters as filters

from .models import Wine


class WineFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr="icontains")
    country = filters.CharFilter(lookup_expr="icontains")
    grape = filters.CharFilter(lookup_expr="icontains")
    rating = filters.NumberFilter()
    rating_min = filters.NumberFilter(field_name="rating", lookup_expr="gte")
    tasting_year = filters.NumberFilter(field_name="tasting_date", lookup_expr="year")

    class Meta:
        model = Wine
        fields = []
