from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, User
from django.utils.safestring import mark_safe
from unfold.admin import ModelAdmin, StackedInline
from unfold.decorators import display
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

from app.profiles.models import Address, Profile
from app.utils import BaseAdmin

admin.site.unregister(User)
admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm

    # Listview
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
        "street",
        "number",
        "neighborhood",
        "complement",
        "city",
        "state",
        "country",
    )


# Admins
@admin.register(Profile)
class ProfileAdmin(BaseAdmin):

    # Listview
    list_display = (
        "see_more",
        "id",
        "user_full_name",
        "user_email",
        "get_type",
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

    # Changeview
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


@admin.register(Address)
class AddressAdmin(BaseAdmin):

    # Listview
    list_display = (
        "see_more",
        "id",
        "full_address",
        "state",
        "country",
    )
    list_filter = BaseAdmin.list_filter + ("state",)

    # Display functions
    @display(description="Endereço")
    def full_address(self, obj):
        return obj.__str__()
