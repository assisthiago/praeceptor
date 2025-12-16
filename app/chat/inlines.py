from django.conf import settings
from unfold.admin import TabularInline

from app.chat.models import Message, ThreadParticipant


class InlineThreadParticipantAdmin(TabularInline):
    model = ThreadParticipant
    tab = True
    extra = 0
    max_num = 0
    fields = readonly_fields = (
        "thread",
        "profile",
        "last_read_at",
        "created_at",
        "updated_at",
        "deleted_at",
    )


class InlineMessageAdmin(TabularInline):
    model = Message
    tab = True
    extra = 0
    max_num = 0
    fields = readonly_fields = (
        "thread",
        "sender",
        "content",
        "created_at",
        "updated_at",
        "deleted_at",
    )
    ordering = ("-created_at",)
    per_page = settings.LIST_PER_PAGE
