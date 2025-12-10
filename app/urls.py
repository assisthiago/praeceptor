from debug_toolbar.toolbar import debug_toolbar_urls
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions, routers

from app.profiles import views as profile_views

# Swagger/OpenAPI 3 schema view
schema_view = get_schema_view(
    openapi.Info(
        title="Snippets API",
        default_version="v1",
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

router = routers.DefaultRouter()
router.register(r"profiles", profile_views.ProfileViewSet)
router.register(r"addresses", profile_views.AddressViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls), name="api"),
]

if settings.DEBUG:
    urlpatterns += [
        path("health/", include("health_check.urls")),
        path("api/auth/", include("rest_framework.urls"), name="api_auth"),
        path("api/swagger.<format>/", schema_view.without_ui(cache_timeout=0), name="schema-json"),
        path("api/swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
        path("api/redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    ] + debug_toolbar_urls()
