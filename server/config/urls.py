from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from .views import server_status

admin.site.site_header = "JourneyHub Administration"
admin.site.index_title = "Admin Services"
admin.site.site_title = "JourneyHub Undo"


urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "api/v1/",
        include(
            [
                path("status/", server_status, name="server status"),
                path("accounts/", include("accounts.urls"), name="accounts"),
                path("journey/", include("journey.urls"), name="journey"),
                path("reaction/", include("reaction.urls"), name="reaction"),
                path("score/", include("score.urls"), name="score"),
                path("audit/", include("audit.urls"), name="audit"),
                path("feed/", include("feed.urls"), name="feed"),
            ]
        ),
    ),
]

if settings.DEBUG:
    urlpatterns += [
        path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
        path(
            "api/docs/",
            SpectacularSwaggerView.as_view(url_name="schema"),
            name="swagger-docs",
        ),
    ]
