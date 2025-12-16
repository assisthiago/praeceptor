from django.contrib import admin
from django.db.models import Count

from app.chat.inlines import InlineMessageAdmin, InlineThreadParticipantAdmin
from app.chat.models import Message, Thread, ThreadParticipant
from app.chat.sections import ThreadParticipantsSection
from app.utils import BaseAdmin


@admin.register(Thread)
class ThreadAdmin(BaseAdmin):

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .prefetch_related(
                "participants",
                "participants__profile",
                "participants__profile__user",
                "messages",
            )
        ).annotate(
            message_count=Count(
                "messages",
                distinct=True,
            ),
        )

    # Changelist
    search_fields = ("uuid",)
    search_help_text = "Pesquisar por UUID."
    list_display = (
        "see_more",
        "id",
        "uuid",
        "get_message_count",
        "group",
    )
    list_filter = BaseAdmin.list_filter + ("group",)
    list_sections = (ThreadParticipantsSection,)

    # Changeform
    fieldsets = (
        (
            "Informações",
            {
                "fields": ("group",),
            },
        ),
        (
            "Auditoria",
            {
                "fields": (
                    "uuid",
                    "created_at",
                    "updated_at",
                    "deleted_at",
                ),
            },
        ),
    )
    inlines = (InlineThreadParticipantAdmin, InlineMessageAdmin)
    readonly_fields = BaseAdmin.readonly_fields + ("uuid",)

    # Display functions
    @admin.display(description="Mensagens")
    def get_message_count(self, obj):
        return obj.message_count


@admin.register(ThreadParticipant)
class ThreadParticipantAdmin(BaseAdmin):

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related(
                "thread",
                "profile",
                "profile__user",
            )
        )

    # Changelist
    search_fields = (
        "thread__uuid",
        "profile__user__first_name",
        "profile__user__last_name",
        "profile__user__email",
    )
    search_help_text = "Pesquisar por UUID, nome ou e-mail."
    list_display = (
        "see_more",
        "id",
        "thread",
        "profile",
        "last_read_at",
    )

    # Changeform
    fieldsets = (
        (
            "Informações",
            {
                "classes": ("tab",),
                "fields": (
                    "thread",
                    "profile",
                    "last_read_at",
                ),
            },
        ),
        (
            "Auditoria",
            {
                "classes": ("tab",),
                "fields": (
                    "uuid",
                    "created_at",
                    "updated_at",
                    "deleted_at",
                ),
            },
        ),
    )
    readonly_fields = BaseAdmin.readonly_fields + (
        "uuid",
        "last_read_at",
    )
    autocomplete_fields = ("profile", "thread")


@admin.register(Message)
class MessageAdmin(BaseAdmin):

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related(
                "thread",
                "sender",
                "sender__user",
            )
        )

    # Changelist
    search_fields = (
        "uuid",
        "sender__user__first_name",
        "sender__user__last_name",
        "sender__user__email",
    )
    search_help_text = "Pesquisar por UUID, nome ou e-mail."
    list_display = (
        "see_more",
        "id",
        "uuid",
        "thread",
        "sender",
    )

    # Changeform
    fieldsets = (
        (
            "Informações",
            {
                "classes": ("tab",),
                "fields": (
                    "thread",
                    "sender",
                    "content",
                ),
            },
        ),
        (
            "Auditoria",
            {
                "classes": ("tab",),
                "fields": (
                    "uuid",
                    "created_at",
                    "updated_at",
                    "deleted_at",
                ),
            },
        ),
    )
    autocomplete_fields = ("thread", "sender")
    readonly_fields = BaseAdmin.readonly_fields + (
        # "thread",
        # "sender",
        # "content",
        "uuid",
    )
