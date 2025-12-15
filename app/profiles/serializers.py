from django.contrib.auth.models import User
from rest_framework import serializers

from app.profiles.models import Address, Profile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
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
        """Format phone as (99) 99999-9999."""
        if len(obj.phone) == 11:
            return f"({obj.phone[:2]}) {obj.phone[2:7]}-{obj.phone[7:]}"
        elif len(obj.phone) == 10:
            return f"({obj.phone[:2]}) {obj.phone[2:6]}-{obj.phone[6:]}"
        return obj.phone

    class Meta:
        model = Profile
        exclude = (
            "cpf",
            "created_at",
            "updated_at",
            "deleted_at",
        )


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
