from pathlib import Path

import dj_database_url
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-4ufc(b5ne_^=z_oe6vin(1x)ai9=k3(!x$4we!r%os3ijb1n13"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    "unfold",  # UNFOLD Admin Panel
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "unfold.contrib.inlines",
    "unfold.contrib.import_export",
    "unfold.contrib.guardian",
    "unfold.contrib.simple_history",
    "unfold.contrib.location_field",
    "unfold.contrib.constance",
    "debug_toolbar",  # Django Debug Toolbar
    "drf_redesign",  # DRF Redesign
    "rest_framework",  # Django REST Framework
    "django_filters",
    "health_check",  # Basic health check
    "health_check.db",
    "health_check.cache",
    "health_check.storage",
    "health_check.contrib.migrations",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "drf_yasg",  # Swagger for DRF
    "app.profiles",
]

MIDDLEWARE = [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "querycount.middleware.QueryCountMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "app.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "app.wsgi.application"

LIST_PER_PAGE = 20

# REST Framework Settings
REST_FRAMEWORK = {
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly"],
    "EXCEPTION_HANDLER": "rest_framework.views.exception_handler",
    "PAGE_SIZE": LIST_PER_PAGE,
}

# Health Check Settings
HEALTH_CHECK = {
    "DISK_USAGE_MAX": 90,  # percent
    "MEMORY_MIN": 100,  # in MB
}

# Django Debug Toolbar Settings
INTERNAL_IPS = ["127.0.0.1"]


# QueryCount Settings
QUERYCOUNT = {
    "THRESHOLDS": {
        "MEDIUM": 10,
        "HIGH": 20,
        "MIN_TIME_TO_LOG": 0,
        "MIN_QUERY_COUNT_TO_LOG": 0,
    },
    "IGNORE_REQUEST_PATTERNS": ["/admin/jsi18n/", "/__debug__/"],
    "IGNORE_SQL_PATTERNS": [],
    "DISPLAY_DUPLICATES": 1,
    "RESPONSE_HEADER": "X-DjangoQueryCount-Count",
}


# UNFOLD Settings
UNFOLD = {
    "SITE_TITLE": "Praeceptor",
    "SITE_HEADER": "Praeceptor",
    "SITE_SUBHEADER": "Painel Administrativo",
    "COLORS": {
        # Blue
        "primary": {
            "50": "oklch(97.7% .014 260)",
            "100": "oklch(94.6% .033 260)",
            "200": "oklch(90.2% .063 260)",
            "300": "oklch(82.7% .119 260)",
            "400": "oklch(71.4% .203 260)",
            "500": "oklch(57.8% .228 260)",
            "600": "oklch(55.8% .250 260)",
            "700": "oklch(49.6% .235 260)",
            "800": "oklch(43.8% .200 260)",
            "900": "oklch(38.1% .170 260)",
            "950": "oklch(29.1% .140 260)",
        },
    },
    "COMMAND": {
        "search_models": True,
        "search_callback": "utils.search_callback",
        "show_history": True,  # Enable history
    },
}

# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases
DATABASE_URL = config("DATABASE_URL", "sqlite:///db.sqlite3")
DATABASES = {
    "default": dj_database_url.config(
        default=DATABASE_URL,
        conn_max_age=600,
        conn_health_checks=True,
    ),
}


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = "pt-br"

TIME_ZONE = "America/Sao_Paulo"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = "static/"


# Geocoding Settings
NOMINATIM_ENDPOINT = "https://nominatim.openstreetmap.org"
VIACEP_ENDPOINT = "https://viacep.com.br/ws"
EARTH_RADIUS_KM = config("EARTH_RADIUS_KM", cast=float, default=6371.0088)
