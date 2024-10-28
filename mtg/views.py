from sqlite3 import IntegrityError

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, JsonResponse

from django.shortcuts import render, get_object_or_404
from django.urls import reverse


from .models import User, Deck, Match


# Create your views here.
def index(request):
    if request.user.is_authenticated:
        return render(request, "mtg/index.html", {
            "user": request.user
        })
    else:
        return HttpResponseRedirect(reverse("mtg:login"))


def login_view(request):
    if request.method == "POST":
        name_or_email = request.POST["name_or_email"]
        password = request.POST["password"]

        try:
            user = User.objects.get(username=name_or_email.capitalize())
        except User.DoesNotExist:
            try:
                user = User.objects.get(email=name_or_email)
            except User.DoesNotExist:
                user = None

        if user:
            user = authenticate(request, username=user.username, password=password)
            login(request, user)
            return HttpResponseRedirect(reverse("mtg:index"))
        else:
            return render(request, "mtg/login.html", {
                "message": "Invalid credentials."
            })
    else:
        return render(request, "mtg/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("mtg:index"))


def register(request):
    if request.method == "POST":
        name = request.POST["name"]
        email = request.POST["email"]

        password = request.POST["password"]
        confirmation = request.POST["confirmation"]

        if password != confirmation:
            return render(request, "mtg/register.html", {
                "message": "Passwords must match."
            })

        try:
            user = User.objects.create_user(name, email, password)
            user.save()
        except IntegrityError:
            return render(request, "mtg/register.html", {
                "message": "User with that email already exists."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("mtg:index"))
    else:
        return render(request, "mtg/register.html")


@login_required
def get_decks(request):
    decks = Deck.objects.all()
    return JsonResponse([deck.serialize() for deck in decks], safe=False)


@login_required
def get_deck_by_id(request, deck_id):
    deck = get_object_or_404(Deck, pk=deck_id)
    return JsonResponse(deck.serialize(), safe=False)


@login_required
def get_decks_by_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    decks = Deck.objects.filter(user=user)
    decks_data = [deck.serialize() for deck in decks]
    print("Get decks user: ", decks_data)
    print("Same, user: ", user.serialize())
    return JsonResponse({
        "decks": decks_data,
        "user": user.serialize()
    }, safe=False)


@login_required
def get_user_by_id(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    return JsonResponse(user.serialize(), safe=False)

@login_required
def get_results(request):
    matches = Match.objects.all()
    match_data = [match.serialize() for match in matches]

    best_player = get_best_n_players(request, n=1)

    best_player_data = best_player[0].serialize() if best_player else {}
    print("Get results DATA: ", best_player_data)

    best_deck = get_best_n_decks(request, n=1)
    print(f"Serializing deck: {best_deck[0].name}, User: {best_deck[0].user}")
    best_deck_data = best_deck[0].serialize() if best_deck else {}
    print("Get results DATA DECK", best_deck_data)

    return JsonResponse({
        "matches": match_data,
        "best_player": best_player_data,
        "best_deck": best_deck_data,
        }, safe=False)

@login_required
def get_results_by_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    matches = Match.objects.filter(user=user)
    matches_data = [match.serialize() for match in matches]
    return JsonResponse({
        "matches": matches_data,
        "user": user.serialize(),
    }, safe=False)



def get_best_n_decks(request, n=1, user_id=None):
    # best_deck = Deck.objects.order_by('-wins_count').first()
    decks = Deck.objects.filter(user=user_id) if user_id else Deck.objects.all()
    sorted_decks = sorted(decks, key=lambda deck: (deck.win_ratio(), deck.total_matches_count), reverse=True)
    best_decks = sorted_decks[:n]
    return best_decks


def get_best_n_players(request, n=1):

    players = User.objects.all()
    player_avg_win_ratio = []

    for player in players:
        player_avg_win_ratio.append((player, player.win_ratio()))

    sorted_players = sorted(player_avg_win_ratio, key=lambda x: x[1], reverse=True)

    for player, avg_win_ratio in sorted_players:
        print(f"Player: {player.username}, Average Win Ratio: {avg_win_ratio}")

    best_n_players = [player[0] for player in sorted_players[:n]]

    print(best_n_players)
    print(type(best_n_players))

    return best_n_players






