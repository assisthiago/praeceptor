from django.conf import settings
from unfold import admin
from unfold.sections import TableSection


class ThreadParticipantsSection(TableSection):

    related_name = "participants"
    fields = readonly_fields = (
        "get_profile",
        "last_read_at",
    )

    # Display
    @admin.display(description="Participantes")
    def get_profile(self, obj):
        return obj.profile.user.get_full_name()
