from django.urls import path

from . import views

app_name = "tournament"

urlpatterns = [
    path("", views.setup, name="setup"),
    path("start", views.start, name="start"),
]