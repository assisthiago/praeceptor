from rest_framework.permissions import AllowAny

from app.profiles.models import Address, Profile
from app.profiles.serializers import AddressSerializer, ProfileSerializer
from app.utils import BaseModelViewSet


class ProfileViewSet(BaseModelViewSet):
    queryset = Profile.objects.select_related("user").prefetch_related("addresses").all()
    serializer_class = ProfileSerializer
    permission_classes = [AllowAny]
    search_fields = filterset_fields = [
        "user__first_name",
        "user__last_name",
        "user__email",
        "type",
        "cpf",
        "phone",
        "birthdate",
    ]


class AddressViewSet(BaseModelViewSet):
    queryset = Address.objects.select_related("profile", "profile__user").all()
    serializer_class = AddressSerializer
    permission_classes = [AllowAny]

    # Filtering
    search_fields = filterset_fields = [
        "zip_code",
        "street",
        "number",
        "neighborhood",
        "complement",
        "city",
        "state",
        "country",
    ]
