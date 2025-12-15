from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from app.profiles.models import Address, Profile
from app.profiles.serializers import (
    AddressSerializer,
    ProfileSerializer,
    SearchProfileSerializer,
)
from app.utils import BaseModelViewSet


class ProfileViewSet(BaseModelViewSet):
    queryset = Profile.objects.select_related("user", "address").all()
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

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "lat",
                openapi.IN_QUERY,
                description="Latitude in decimal degrees",
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                "lon",
                openapi.IN_QUERY,
                description="Longitude in decimal degrees",
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                "radius_km",
                openapi.IN_QUERY,
                description="Search radius in kilometers",
                type=openapi.TYPE_STRING,
                required=False,
                default=10.0,
            ),
        ],
    )
    @action(
        detail=False,
        methods=["get"],
        permission_classes=[AllowAny],
        url_path="search",
        url_name="search",
    )
    def search(self, request, *args, **kwargs):
        """Search instructors by proximity given lat, lon, and radius_km query params."""
        params = SearchProfileSerializer(data=request.query_params)
        params.is_valid(raise_exception=True)

        instructors = Profile.find_nearby_instructors(
            lat=float(params.validated_data["lat"]),
            lon=float(params.validated_data["lon"]),
            radius_km=float(params.validated_data["radius_km"]),
        )

        # No instructors found
        if not instructors:
            return Response(
                {"detail": "No instructors found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Paginate results
        if page := self.paginate_queryset(instructors):
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        # Serialize full results
        serializer = self.get_serializer(instructors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


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
