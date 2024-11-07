from django.urls import path

from . import views

app_name = "tournament"

urlpatterns = [
    path("", views.setup, name="setup"),
    path("start", views.start, name="start"),
    path("round/<int:n_round>", views.play_round, name="play_round"),
    path("get_possible_results", views.get_possible_results, name="get_possible_results"),
    path("next_round", views.next_round, name="next_round"),
]