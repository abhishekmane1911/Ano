from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.db import connection


def health_check(request):
    """Health check endpoint for monitoring"""
    try:
        # Check database connection
        connection.ensure_connection()
        return JsonResponse({"status": "healthy", "database": "connected"})
    except Exception as e:
        return JsonResponse(
            {"status": "unhealthy", "error": str(e)}, status=503
        )


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health_check, name="health_check"),

    path("api/monitoring/", include("ano_backend.health_urls")),
    path("api/auth/", include("authentication.urls")),
    path("api/profiles/", include("profiles.urls")),
    path("api/chat/", include("chat.urls")),
    path("api/matchmaking/", include("matchmaking.urls")),
    path("api/reports/", include("reports.urls")),
    path("api/admin/", include("admin_dashboard.urls")),
 
    path("api/reputation/", include("reputation.urls")),
    path("api/moderation/", include("moderation.urls")),
    path("api/security/", include("security.urls")),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
