import uuid

from django.db import models

from app.profiles.models import Profile
from app.utils import SoftDeleteModel, TimestampedModel


class Thread(TimestampedModel, SoftDeleteModel):

    # Fields
    group = models.BooleanField(
        verbose_name="grupo",
        default=False,
    )
    uuid = models.UUIDField(
        verbose_name="UUID",
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )

    class Meta:
        verbose_name = "conversa"
        verbose_name_plural = "conversas"
        db_table = "thread"

    def __str__(self):
        return str(self.uuid)


class ThreadParticipant(TimestampedModel, SoftDeleteModel):

    # Relations
    thread = models.ForeignKey(
        Thread,
        verbose_name="conversa",
        related_name="participants",
        on_delete=models.CASCADE,
    )
    profile = models.ForeignKey(
        Profile,
        verbose_name="perfil",
        related_name="threads",
        on_delete=models.CASCADE,
    )

    # Fields
    uuid = models.UUIDField(
        verbose_name="UUID",
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )
    last_read_at = models.DateTimeField(
        verbose_name="última leitura em",
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "participante da conversa"
        verbose_name_plural = "participantes da conversa"
        db_table = "thread_participant"
        constraints = [
            models.UniqueConstraint(
                fields=["thread", "profile"],
                name="unique_thread_profile",
            ),
        ]
        indexes = [models.Index(fields=["thread", "profile"])]

    def __str__(self):
        return f"{str(self.thread)} | {str(self.profile)}"


class Message(TimestampedModel, SoftDeleteModel):

    # Relations
    thread = models.ForeignKey(
        Thread,
        verbose_name="conversa",
        related_name="messages",
        on_delete=models.CASCADE,
    )
    sender = models.ForeignKey(
        Profile,
        verbose_name="remetente",
        related_name="sent_messages",
        on_delete=models.CASCADE,
    )

    # Fields
    content = models.TextField(verbose_name="conteúdo")
    uuid = models.UUIDField(
        verbose_name="UUID",
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )

    class Meta:
        verbose_name = "mensagem"
        verbose_name_plural = "mensagens"
        db_table = "message"
        indexes = [
            models.Index(fields=["thread", "-created_at"]),
            models.Index(fields=["sender", "-created_at"]),
        ]

    def __str__(self):
        return str(self.uuid)
