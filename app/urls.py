from debug_toolbar.toolbar import debug_toolbar_urls
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers

from app.chat import views as chat_views
from app.documentation import schema_view
from app.profiles import views as profile_views

router = routers.DefaultRouter()

# Chat app
router.register(
    r"threads",
    chat_views.ThreadViewSet,
    basename="thread",
)
router.register(
    r"thread-participants",
    chat_views.ThreadParticipantViewSet,
    basename="threadparticipant",
)
router.register(
    r"messages",
    chat_views.MessageViewSet,
    basename="message",
)

# Profile app
router.register(
    r"profiles",
    profile_views.ProfileViewSet,
    basename="profile",
)
router.register(
    r"addresses",
    profile_views.AddressViewSet,
    basename="address",
)


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
