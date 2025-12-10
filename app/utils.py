from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.safestring import mark_safe
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
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


# Abstract rest framework ModelViewSet
class BaseModelViewSet(viewsets.ModelViewSet):
    """Base viewset with common configurations."""

    filter_backends = [
        filters.SearchFilter,
        DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    ordering_fields = "__all__"
    ordering = ["-created_at"]
