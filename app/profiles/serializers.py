from django.contrib.auth.models import User
from rest_framework import serializers

from app.profiles.models import Address, Profile
from app.utils import format_phone


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
        )


class AddressSerializer(serializers.ModelSerializer):

    zip_code = serializers.SerializerMethodField(
        method_name="zip_code_formatted",
        read_only=True,
    )

    # Custom fields
    def zip_code_formatted(self, obj):
        """Format zip code as 99999-999."""
        return f"{obj.zip_code[:5]}-{obj.zip_code[5:]}"

    class Meta:
        model = Address
        exclude = (
            "id",
            "profile",
            "number",
            "complement",
            "latitude",
            "longitude",
            "created_at",
            "updated_at",
            "deleted_at",
        )


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False)
    address = AddressSerializer(many=False)
    phone = serializers.SerializerMethodField(
        method_name="phone_formatted",
        read_only=True,
    )
    birthdate = serializers.DateField(format="%d/%m/%Y")

    # Custom fields
    def phone_formatted(self, obj):
        return format_phone(self, obj)

    class Meta:
        model = Profile
        exclude = (
            "id",
            "cpf",
            "created_at",
            "updated_at",
            "deleted_at",
        )


class SimpleProfileSerializer(serializers.ModelSerializer):

    user = UserSerializer(many=False, read_only=True)
    phone = serializers.SerializerMethodField(
        method_name="phone_formatted",
        read_only=True,
    )

    class Meta:
        model = Profile
        fields = (
            "user",
            "phone",
            "type",
        )

    # Custom fields
    def phone_formatted(self, obj):
        return format_phone(self, obj)


class SearchProfileSerializer(serializers.Serializer):
    lat = serializers.CharField()
    lon = serializers.CharField()
    radius_km = serializers.FloatField(default=10.0)

    # Validators
    def validate_lat(self, value):
        # Replace comma with period for decimal separator
        normalized_value = value.replace(",", ".")
        try:
            lat_float = float(normalized_value)
            if not -90 <= lat_float <= 90:
                raise serializers.ValidationError("Latitude must be between -90 and 90 degrees.")
            return normalized_value
        except ValueError:
            raise serializers.ValidationError("Invalid latitude format.")

    def validate_lon(self, value):
        # Replace comma with period for decimal separator
        normalized_value = value.replace(",", ".")
        try:
            lon_float = float(normalized_value)
            if not -180 <= lon_float <= 180:
                raise serializers.ValidationError("Longitude must be between -180 and 180 degrees.")
            return normalized_value
        except ValueError:
            raise serializers.ValidationError("Invalid longitude format.")
