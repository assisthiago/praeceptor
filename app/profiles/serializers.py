from rest_framework import serializers

from app.profiles.models import Address, Profile


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        exclude = ("profile", "created_at", "updated_at", "deleted_at")


class ProfileSerializer(serializers.ModelSerializer):
    addresses = AddressSerializer(many=True)

    class Meta:
        model = Profile
        exclude = ("created_at", "updated_at", "deleted_at")
