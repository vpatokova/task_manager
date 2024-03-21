from pathlib import Path
import socket

from django.utils.translation import gettext_lazy as _
import environ

BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()
environ.Env.read_env()

SECRET_KEY = env.str("SECRET_KEY", default="secret_key")

DEBUG = env.bool("DEBUG", default=False)

USER_IS_ACTIVE = env.bool("USER_IS_ACTIVE", default=DEBUG)

INSTALLED_APPS = [
    # django apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # third-party apps
    "debug_toolbar",
    "django_cleanup",
    "sorl.thumbnail",
    "webpush",
    # our apps
    "core.apps.CoreConfig",
    "feedback.apps.FeedbackConfig",
    "homepage.apps.HomepageConfig",
    "tasks.apps.TasksConfig",
    "users.apps.UsersConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "tasks.middlewares.TimezoneMiddleware",
]

ROOT_URLCONF = "task_manager.urls"

WSGI_APPLICATION = "task_manager.wsgi.application"
ASGI_APPLICATION = "task_manager.asgi.application"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": env.str("DJANGO_DATABASE_NAME"),
        "USER": env.str("DJANGO_DATABASE_USER"),
        "PASSWORD": env.str("DJANGO_DATABASE_PASSWORD"),
        "HOST": env.str("DJANGO_DATABASE_HOST"),
        "PORT": env.str("DJANGO_DATABASE_PORT"),
        "OPTIONS": {
            "connect_timeout": 10,
        },
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation."
        "UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation."
        "MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation."
        "CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation."
        "NumericPasswordValidator",
    },
]

TIME_ZONE = "Asia/Yekaterinburg"
USE_TZ = True

LANGUAGE_CODE = "ru"

USE_I18N = True
STATIC_URL = "static/"

LOCALE_PATHS = [
    BASE_DIR / "locale",
]

LANGUAGES = [
    ("en", _("English")),
    ("ru", _("Russian")),
]

STATICFILES_DIRS = [BASE_DIR / "static_dev"]

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

TEMPLATE_DIRS = [BASE_DIR / "templates"]
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": TEMPLATE_DIRS,
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "tasks.context_processors.user_tz",
            ],
        },
    },
]

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])
try:
    INTERNAL_IPS = [
        "{0}.1".format(ip[: ip.rfind(".")])
        for ip in socket.gethostbyname_ex(socket.gethostname())[2]
    ]
except socket.error:
    INTERNAL_IPS = []
INTERNAL_IPS += ["127.0.0.1", "10.0.2.2", "localhost"]

if env.str("EMAIL_HOST_USER", default=None) and env.str(
    "EMAIL_HOST_PASSWORD", default=None
):
    EMAIL_HOST_USER = env.str("EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD = env.str("EMAIL_HOST_PASSWORD")
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = "smtp.gmail.com"
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
else:
    EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
    EMAIL_FILE_PATH = BASE_DIR / "sent_emails"
    EMAIL_HOST_USER = env.str("EMAIL_HOST_USER", default="yandex@yandex.ru")

AUTHENTICATION_BACKENDS = [
    "users.backends.EmailBackend",
]

LOGIN_URL = "/auth/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/auth/logout_success/"
MAX_LOGIN_ATTEMPTS = 3

WEBPUSH_SETTINGS = {
    "VAPID_PUBLIC_KEY": env.str(
        "VAPID_PUBLIC_KEY",
        default="BDPHx7wL3tlJ7w10eY2_LKKTXqPLd0v_s7wWCTmvSkItrHMT1MKIvvzhqEY-z"
        "gfkMUEso9dO49_h30xR3YOLAa0",
    ),
    "VAPID_PRIVATE_KEY": env.str(
        "VAPID_PRIVATE_KEY",
        default="obcZws2OiAwK_UscXidM7XaH7SOJEjCYuevvvWdvb2Y",
    ),
    "VAPID_ADMIN_EMAIL": env.str(
        "VAPID_ADMIN_EMAIL", default="yandex@yandex.ru"
    ),
}

ABSOLUTE_URL = "http://localhost"
PORT = 8000

REDIS_HOST = env.str("REDIS_HOST", default="tasks-broker")
REDIS_PORT = env.int("REDIS_PORT", default=6379)

CELERY_BROKER_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
CELERY_RESULT_BACKEND = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(REDIS_HOST, REDIS_PORT)],
        },
    },
}
