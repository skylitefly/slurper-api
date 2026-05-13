from django.urls import include, path

from slurper import views

urlpatterns = [
    path("healthz/", views.health, name="health"),
    path("api/", include("slurper.urls")),
    path("", include("slurper.urls")),
]
