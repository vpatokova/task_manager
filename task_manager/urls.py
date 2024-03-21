from django import get_version
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.decorators.cache import cache_page
from django.views.i18n import JavaScriptCatalog

urlpatterns = [
    path("", include("homepage.urls")),
    path("admin/", admin.site.urls),
    path("auth/", include("users.urls")),
    path("auth/", include("django.contrib.auth.urls")),
    path("feedback/", include("feedback.urls")),
    path(
        "jsi18n/",
        cache_page(60 * 60 * 24, key_prefix=f"jsi18n-{get_version()}")(
            JavaScriptCatalog.as_view(),
        ),
        name="javascript-catalog",
    ),
    path("tasks/", include("tasks.urls")),
    re_path(r"^webpush/", include("webpush.urls")),
]
if settings.DEBUG:
    import debug_toolbar

    urlpatterns += (path("__debug__/", include(debug_toolbar.urls)),)
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
