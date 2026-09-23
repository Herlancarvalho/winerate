from django.conf import settings
from rest_framework import serializers

from .models import Wine


class WineSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(min_value=1, max_value=5)

    class Meta:
        model = Wine
        # `user` não está na lista: o dono é sempre definido no servidor
        fields = (
            "id", "name", "winery", "vintage", "country", "region", "grape",
            "price", "location", "rating", "comment", "tasting_date",
            "created_at", "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class LabelImageSerializer(serializers.Serializer):
    image = serializers.ImageField()

    def validate_image(self, image):
        if image.size > settings.LABEL_IMAGE_MAX_BYTES:
            raise serializers.ValidationError("A imagem excede o tamanho máximo de 5 MB.")
        # O ImageField do Django define content_type a partir do formato
        # detectado pelo Pillow, não do cabeçalho enviado pelo cliente.
        if getattr(image, "content_type", None) not in settings.LABEL_IMAGE_ALLOWED_TYPES:
            raise serializers.ValidationError("Formato não suportado. Use JPEG, PNG ou WebP.")
        return image
