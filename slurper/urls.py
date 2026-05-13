from django.urls import path

from . import views

app_name = "slurper"

urlpatterns = [
    path("users/info/", views.users_info, name="users-info"),
]
