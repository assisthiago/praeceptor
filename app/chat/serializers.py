from rest_framework import serializers

from app.chat.models import Message, Thread, ThreadParticipant
from app.profiles.serializers import SimpleProfileSerializer


class ThreadParticipantSerializer(serializers.ModelSerializer):

    profile = SimpleProfileSerializer(many=False, read_only=True)

    class Meta:
        model = ThreadParticipant
        exclude = (
            "id",
            "created_at",
            "updated_at",
            "deleted_at",
        )


class MessageSerializer(serializers.ModelSerializer):

    sender = SimpleProfileSerializer(many=False, read_only=True)

    class Meta:
        model = Message
        exclude = (
            "id",
            "thread",
        )


class ThreadSerializer(serializers.ModelSerializer):

    participants = ThreadParticipantSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Thread
        exclude = ("id",)
