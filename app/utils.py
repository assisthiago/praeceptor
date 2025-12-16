import math
import uuid as _uuid

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.safestring import mark_safe
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import RangeDateFilter
from unfold.decorators import display


# Abstract base classes for shared fields
class TimestampedModel(models.Model):
    """Abstract base class that provides self-updating 'created_at' and 'updated_at' fields."""

    created_at = models.DateTimeField(verbose_name="criado em", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="atualizado em", auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    """Abstract base class that provides a 'deleted_at' field for soft deletion."""

    deleted_at = models.DateTimeField(verbose_name="deletado em", blank=True, null=True)

    class Meta:
        abstract = True

    def delete(self, *args, **kwargs):
        """Soft delete the object by setting 'deleted_at' timestamp instead of deleting from the database."""
        self.deleted_at = timezone.now()
        self.save()


class BaseAdmin(ModelAdmin):
    """Base admin class with common configurations."""

    list_per_page = settings.LIST_PER_PAGE

    list_filter = (
        ("created_at", RangeDateFilter),
        ("updated_at", RangeDateFilter),
        ("deleted_at", RangeDateFilter),
    )

    readonly_fields = ("created_at", "updated_at", "deleted_at")

    @display(description="")
    def see_more(self, obj):
        return mark_safe('<span class="material-symbols-outlined">visibility</span>')


# ==============================================================================


# Abstract rest framework ModelViewSet
class LookupIdOrUuidMixin:
    """Mixin to allow lookup by either ID (pk) or UUID field."""

    uuid_field_name = "uuid"  # padrão do nome do campo

    def _is_uuid(self, value: str) -> bool:
        """Check if the given value is a valid UUID."""
        try:
            _uuid.UUID(str(value))
            return True
        except Exception:
            return False

    def _model_has_uuid_field(self) -> bool:
        """Check if the model has the specified UUID field."""
        model = self.get_queryset().model
        try:
            model._meta.get_field(self.uuid_field_name)
            return True
        except Exception:
            return False

    def get_object(self):
        """Retrieve the object based on either UUID or ID."""
        queryset = self.filter_queryset(self.get_queryset())

        lookup_kwarg = self.lookup_url_kwarg or self.lookup_field  # normalmente "pk"
        lookup_value = self.kwargs.get(lookup_kwarg)

        if lookup_value is None:
            raise AssertionError("Lookup value not found in URL kwargs.")

        if self._model_has_uuid_field() and self._is_uuid(lookup_value):
            obj = get_object_or_404(queryset, **{self.uuid_field_name: lookup_value})
        else:
            obj = get_object_or_404(queryset, pk=lookup_value)

        self.check_object_permissions(self.request, obj)
        return obj


class BaseModelViewSet(LookupIdOrUuidMixin, viewsets.ModelViewSet):
    """Base viewset with common configurations."""

    permission_classes = [AllowAny]  # Default permission, can be overridden in subclasses
    lookup_value_regex = r"(?:\d+|[0-9a-fA-F-]{36})"  # Accept both integer IDs and UUIDs

    # Default filter backends and ordering
    filter_backends = [
        filters.SearchFilter,
        DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    ordering_fields = "__all__"
    ordering = ["-created_at"]


# ==============================================================================


# Geographical functions
def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great-circle distance between two points on the Earth surface.

    Args:
        lat1 (float): Latitude of the first point in decimal degrees.
        lon1 (float): Longitude of the first point in decimal degrees.
        lat2 (float): Latitude of the second point in decimal degrees.
        lon2 (float): Longitude of the second point in decimal degrees.

    Returns:
        float: Distance between the two points in kilometers.
    """
    # Convert decimal degrees to radians
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    # Haversine formula
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return settings.EARTH_RADIUS_KM * c


def bounding_box(lat: float, lon: float, radius_km: float) -> tuple[float, float, float, float]:
    """Pre-filtering bounding box for a given point and radius.

    Args:
        lat (float): Latitude of the point in decimal degrees.
        lon (float): Longitude of the point in decimal degrees.
        radius_km (float): Radius in kilometers.

    Returns:
        tuple[float, float, float, float]: Bounding box as (min_lat, max_lat, min_lon, max_lon).
    """
    lat_delta = radius_km / 110.574  # 1st degree of latitude ~ 110.574 km
    cos_lat = math.cos(math.radians(lat))  # 1st degree of longitude ~ 111.320*cos(latitude) km
    lon_delta = radius_km / (111.320 * max(cos_lat, 1e-6))  # Avoid division by zero at poles
    return (lat - lat_delta, lat + lat_delta, lon - lon_delta, lon + lon_delta)


# ==============================================================================


# Format functions
def format_phone(obj: models.Model) -> str:
    """Format phone number into standard representation.
    (999) 99999-9999 or (99) 9999-9999

    Args:
        obj (models.Model): Object with 'phone' attribute.

    Returns:
        str: Formatted phone number.
    """
    if len(obj.phone) == 11:
        return f"({obj.phone[:2]}) {obj.phone[2:7]}-{obj.phone[7:]}"
    elif len(obj.phone) == 10:
        return f"({obj.phone[:2]}) {obj.phone[2:6]}-{obj.phone[6:]}"
    return obj.phone
