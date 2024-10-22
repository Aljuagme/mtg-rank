from django.urls import path

from . import views

app_name = "mtg"

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("get_decks", views.get_decks, name="get_decks"),
    path("get_deck/<int:deck_id>", views.get_deck_by_id, name="get_deck_by_id"),
    path("get_results", views.get_results, name="get_results"),
    path("get_decks/<int:user_id>", views.get_decks_by_user, name="get_decks_by_user"),
    path("get_results/<int:user_id>", views.get_results_by_user, name="get_results_by_user"),
]