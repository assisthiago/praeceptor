import re

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

from app.api import NominatimAPI, ViaCEPAPI
from app.utils import SoftDeleteModel, TimestampedModel, bounding_box, haversine_km


class Profile(TimestampedModel, SoftDeleteModel):

    TYPE_CLIENT = "client"
    TYPE_INSTRUCTOR = "instructor"
    TYPE_CHOICES = (
        (TYPE_CLIENT, "Cliente"),
        (TYPE_INSTRUCTOR, "Instrutor"),
    )

    # Relations
    user = models.OneToOneField(
        User,
        verbose_name="usuário",
        related_name="client",
        on_delete=models.CASCADE,
    )

    # Fields
    type = models.CharField(
        verbose_name="tipo",
        max_length=10,
        choices=TYPE_CHOICES,
    )
    cpf = models.CharField(verbose_name="CPF", unique=True, max_length=11)
    phone = models.CharField(verbose_name="telefone", unique=True, max_length=13)
    birthdate = models.DateField(verbose_name="data de nascimento")

    def save(self, *args, **kwargs):
        if not self.address.latitude or not self.address.longitude:
            try:
                lat, lon = NominatimAPI.search(self.address.zip_code)
                if isinstance(lat, float) and isinstance(lon, float):
                    self.address.latitude = lat
                    self.address.longitude = lon
            except Exception:
                print("Error geocoding address")

        if not self.address.street or not self.address.neighborhood or not self.address.city or not self.address.state:
            try:
                address_data = ViaCEPAPI.search(self.address.zip_code)
                if isinstance(address_data, dict):
                    self.address.street = address_data.get("street")
                    self.address.neighborhood = address_data.get("neighborhood")
                    self.address.city = address_data.get("city")
                    self.address.state = address_data.get("state")
                    self.address.region = address_data.get("region")
                    self.address.country = address_data.get("country")
            except Exception:
                print("Error fetching address data")

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "perfil"
        verbose_name_plural = "perfis"
        db_table = "profile"

    @staticmethod
    def find_nearby_instructors(
        lat: float,
        lon: float,
        radius_km: float = 10.0,
        qs=None,
    ) -> list["Profile"]:
        """Find instructors within a certain radius from a given point.

        Args:
            lat (float): Latitude of the center point in decimal degrees.
            lon (float): Longitude of the center point in decimal degrees.
            radius_km (float, optional): Search radius in kilometers. Defaults to 10.0.
            qs (models.QuerySet["Profile"], optional): Base queryset to filter from. Defaults to None.

        Returns:
            list["Profile"]: A list of instructors within the specified radius.
        """

        if qs is None:
            qs = Profile.objects.filter(type=Profile.TYPE_INSTRUCTOR)

        min_lat, max_lat, min_lon, max_lon = bounding_box(lat, lon, radius_km)

        # Pre-filter candidates within the bounding box
        candidates = qs.select_related("address").filter(
            address__latitude__isnull=False,
            address__longitude__isnull=False,
            address__latitude__gte=min_lat,
            address__latitude__lte=max_lat,
            address__longitude__gte=min_lon,
            address__longitude__lte=max_lon,
        )

        result = []
        for profile in candidates:
            # Calculate precise distance
            a = profile.address
            d = haversine_km(lat, lon, a.latitude, a.longitude)
            if d <= radius_km:
                result.append(profile)

        return result

    def __str__(self):
        return self.user.get_full_name()


class Address(TimestampedModel, SoftDeleteModel):

    # Relations
    profile = models.OneToOneField(
        Profile,
        verbose_name="perfil",
        related_name="address",
        on_delete=models.CASCADE,
    )

    # Fields
    zip_code = models.CharField(verbose_name="CEP", db_index=True, max_length=20)

    # Fields from ViaCEP
    street = models.CharField(verbose_name="logradouro", max_length=255, blank=True, null=True)
    number = models.CharField(verbose_name="número", max_length=10, blank=True, null=True)
    neighborhood = models.CharField(verbose_name="bairro", max_length=255, blank=True, null=True)
    complement = models.TextField(verbose_name="complemento", max_length=255, blank=True, null=True)
    city = models.CharField(verbose_name="cidade", max_length=255, blank=True, null=True)
    state = models.CharField(verbose_name="estado", max_length=255, blank=True, null=True)
    region = models.CharField(verbose_name="região", max_length=255, blank=True, null=True)
    country = models.CharField(verbose_name="país", max_length=255, blank=True, null=True)

    # Fields from geocoding via NominatimAPI
    latitude = models.FloatField(verbose_name="latitude", db_index=True, blank=True, null=True)
    longitude = models.FloatField(verbose_name="longitude", db_index=True, blank=True, null=True)

    class Meta:
        verbose_name = "endereço"
        verbose_name_plural = "endereços"
        db_table = "address"

    def save(self, *args, **kwargs):
        if not self.latitude or not self.longitude:
            try:
                lat, lon = NominatimAPI.search(self.zip_code)
                if isinstance(lat, float) and isinstance(lon, float):
                    self.latitude = lat
                    self.longitude = lon
            except Exception:
                print("Error geocoding address")

        if not self.street or not self.neighborhood or not self.city or not self.state:
            try:
                address_data = ViaCEPAPI.search(self.zip_code)
                if isinstance(address_data, dict):
                    self.street = address_data.get("street")
                    self.neighborhood = address_data.get("neighborhood")
                    self.city = address_data.get("city")
                    self.state = address_data.get("state")
                    self.region = address_data.get("region")
                    self.country = address_data.get("country")
            except Exception:
                print("Error fetching address data")

        super().save(*args, **kwargs)

    def format_zip_code(self):
        return re.sub(r"(\d{5})(\d{3})", r"\1-\2", self.zip_code)

    def __str__(self):
        if not self.street:
            return f"{self.format_zip_code()}"
        return f"{self.street}{f', {self.number}' if self.number else ''} - {self.neighborhood}, {self.city} - {self.state}, {self.zip_code}"
