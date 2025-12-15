from django.conf import settings
from django.contrib import admin, messages
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, User
from django.utils.safestring import mark_safe
from unfold.admin import ModelAdmin, StackedInline
from unfold.decorators import action, display
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

from app.api import NominatimAPI, ViaCEPAPI
from app.profiles.models import Address, Profile
from app.utils import BaseAdmin

admin.site.unregister(User)
admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm

    # Changelist
    list_display = (
        "see_more",
        "id",
        "email",
        "first_name",
        "last_name",
        "is_active",
        "is_staff",
    )
    list_filter = (
        "is_staff",
        "is_superuser",
        "is_active",
        "groups",
    )
    search_fields = (
        "first_name",
        "last_name",
        "email",
    )
    search_help_text = "Buscar por nome de usuário, nome, sobrenome ou e-mail"

    @display(description="")
    def see_more(self, obj):
        return mark_safe('<span class="material-symbols-outlined">visibility</span>')


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass


# Inlines
class AddressInline(StackedInline):
    model = Address
    extra = 1
    max_num = 1
    tab = True
    fields = (
        "zip_code",
        "latitude",
        "longitude",
        "street",
        "number",
        "neighborhood",
        "complement",
        "city",
        "state",
        "region",
        "country",
    )
    readonly_fields = ("latitude", "longitude")


# Admins
@admin.register(Profile)
class ProfileAdmin(BaseAdmin):

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user").select_related("address")

    # Changelist
    list_display = (
        "see_more",
        "id",
        "user_full_name",
        "user_email",
        "get_type",
        "is_zip_code_valid",
    )
    search_fields = (
        "user__first_name",
        "user__last_name",
        "user__email",
        "cpf",
        "phone",
    )
    search_help_text = "Buscar por nome, e-mail, cpf ou telefone"
    list_filter = BaseAdmin.list_filter + ("type",)
    actions_row = ["geocode_cep_nominatim", "get_cep_viacep"]

    # Changeform
    inlines = (AddressInline,)
    fieldsets = (
        (
            "Informações",
            {
                "classes": ("tab",),
                "fields": (
                    "user",
                    "type",
                    "cpf",
                    "phone",
                    "birthdate",
                ),
            },
        ),
        (
            "Auditoria",
            {
                "classes": ("tab",),
                "fields": (
                    "created_at",
                    "updated_at",
                    "deleted_at",
                ),
            },
        ),
    )

    # Display functions
    @display(description="Nome")
    def user_full_name(self, obj):
        return obj.user.get_full_name()

    @display(description="E-mail")
    def user_email(self, obj):
        return obj.user.email

    @display(
        description="Tipo",
        label={
            Profile.TYPE_CLIENT: "primary",
            Profile.TYPE_INSTRUCTOR: "success",
        },
    )
    def get_type(self, obj):
        return obj.type, obj.get_type_display()

    @display(description="CEP", label={0: "danger", 1: "warning", 2: "success"})
    def is_zip_code_valid(self, obj):
        value = 0
        value += 1 if obj.address.zip_code and obj.address.latitude else 0
        value += 1 if obj.address.zip_code and obj.address.longitude else 0
        return value, ["Não", "Parcial", "Sim"][value]

    # Actions
    @action(description="Geocodificar CEP via Nominatim")
    def geocode_cep_nominatim(self, request, object_id):
        profile = self.get_object(request, object_id)
        address = profile.address
        lat, lon = NominatimAPI.search(zip_code=address.zip_code)

        if isinstance(lat, float) and isinstance(lon, float):
            address.latitude = lat
            address.longitude = lon
            address.save()
            self.message_user(
                request,
                "CEP geocodificado com sucesso.",
                messages.SUCCESS,
            )

        else:
            self.message_user(
                request,
                f"Falha ao geocodificar o CEP: {address.zip_code}.",
                messages.ERROR,
            )

    @action(description="Consultar CEP via ViaCEP")
    def get_cep_viacep(self, request, object_id):
        profile = self.get_object(request, object_id)
        address = profile.address
        address_data = ViaCEPAPI.search(zip_code="21645010")

        if address_data:
            address.street = address_data.get("street")
            address.neighborhood = address_data.get("neighborhood")
            address.city = address_data.get("city")
            address.state = address_data.get("state")
            address.country = "Brasil"
            address.save()
            self.message_user(
                request,
                "CEP consultado com sucesso.",
                messages.SUCCESS,
            )

        else:
            self.message_user(
                request,
                f"Falha ao consultar o CEP: {address.zip_code}.",
                messages.ERROR,
            )


@admin.register(Address)
class AddressAdmin(BaseAdmin):

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("profile", "profile__user")

    # Changelist
    list_display = (
        "see_more",
        "id",
        "full_address",
        "state",
        "country",
    )
    list_filter = BaseAdmin.list_filter + ("state",)

    # Changeform
    fieldsets = (
        (
            "Informações",
            {
                "classes": ("tab",),
                "fields": (
                    "profile",
                    "zip_code",
                    "street",
                    "number",
                    "neighborhood",
                    "complement",
                    "city",
                    "state",
                    "country",
                ),
            },
        ),
        (
            "Auditoria",
            {
                "classes": ("tab",),
                "fields": (
                    "created_at",
                    "updated_at",
                    "deleted_at",
                ),
            },
        ),
    )
    readonly_fields = BaseAdmin.readonly_fields + ("profile",)

    # Display functions
    @display(description="Endereço")
    def full_address(self, obj):
        return str(obj)
