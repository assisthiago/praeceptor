from django.contrib.auth.models import User
from django.db import models

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
    cpf = models.CharField(verbose_name="cpf", max_length=14)
    phone = models.CharField(verbose_name="telefone", max_length=20)
    birthdate = models.DateField(verbose_name="data de nascimento")

    class Meta:
        verbose_name = "perfil"
        verbose_name_plural = "perfis"
        db_table = "profile"

    def __str__(self):
        return self.user.get_full_name()


class Address(TimestampedModel, SoftDeleteModel):

    # Relations
    profile = models.ForeignKey(
        Profile,
        verbose_name="perfil",
        related_name="addresses",
        on_delete=models.CASCADE,
    )

    # Fields
    zip_code = models.CharField(verbose_name="cep", max_length=20)
    street = models.CharField(verbose_name="rua", max_length=255)
    number = models.CharField(verbose_name="número", max_length=20)
    neighborhood = models.CharField(verbose_name="bairro", max_length=100)
    complement = models.TextField(verbose_name="complemento", max_length=255, blank=True, null=True)
    city = models.CharField(verbose_name="cidade", max_length=100)
    state = models.CharField(verbose_name="estado", max_length=100)
    country = models.CharField(verbose_name="país", max_length=100)

    class Meta:
        verbose_name = "endereço"
        verbose_name_plural = "endereços"
        db_table = "address"

    def __str__(self):
        return f"{self.street}, {self.number} - {self.neighborhood}, {self.city} - {self.state}, {self.zip_code}"
