import re

from django.contrib.auth.models import User
from django.db import models

from app.api import NominatimAPI, ViaCEPAPI
from app.utils import SoftDeleteModel, TimestampedModel


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
    cpf = models.CharField(verbose_name="cpf", unique=True, max_length=11)
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
    zip_code = models.CharField(verbose_name="cep", db_index=True, max_length=20)

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
    latitude = models.FloatField(verbose_name="latitude", blank=True, null=True)
    longitude = models.FloatField(verbose_name="longitude", blank=True, null=True)

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
