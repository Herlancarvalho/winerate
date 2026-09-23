from django.contrib import admin

from .models import Wine


@admin.register(Wine)
class WineAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "rating", "tasting_date", "country")
    list_filter = ("rating", "country")
    search_fields = ("name", "winery", "user__email")
