from app.chat.models import Message, Thread, ThreadParticipant
from app.chat.serializers import (
    MessageSerializer,
    ThreadParticipantSerializer,
    ThreadSerializer,
)
from app.utils import BaseModelViewSet


class ThreadViewSet(BaseModelViewSet):
    queryset = Thread.objects.prefetch_related(
        "participants",
        "participants__profile",
        "participants__profile__user",
        "messages",
    ).all()
    serializer_class = ThreadSerializer
    search_fields = filterset_fields = ["group"]


class ThreadParticipantViewSet(BaseModelViewSet):
    queryset = ThreadParticipant.objects.select_related(
        "thread",
        "profile",
        "profile__user",
    ).all()
    serializer_class = ThreadParticipantSerializer
    search_fields = filterset_fields = ["thread", "profile"]


class MessageViewSet(BaseModelViewSet):
    queryset = Message.objects.select_related(
        "thread",
        "sender",
        "sender__user",
    ).all()
    serializer_class = MessageSerializer
    search_fields = filterset_fields = ["thread", "sender"]
