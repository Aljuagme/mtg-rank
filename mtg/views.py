import json
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

    decks_sorted = sorted(decks, key= lambda deck: (deck.win_ratio(), deck.total_matches_count), reverse=True)
    decks_data = [deck.serialize() for deck in decks_sorted]

    no_user_decks = Deck.objects.exclude(user=user)
    no_user_decks_data = [deck.serialize() for deck in no_user_decks]

    return JsonResponse({
        "decks": decks_data,
        "no_user_decks": no_user_decks_data,
        "user": user.serialize()
    }, safe=False)


@login_required
def get_user_by_id(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    return JsonResponse(user.serialize(), safe=False)


@login_required
def get_logged_in_user(request):
    return JsonResponse({
        "name": request.user.username,
        "id": request.user.id})


@login_required
def get_results(request):
    matches = Match.objects.all()
    match_data = [match.serialize() for match in matches][:10]

    best_player = json.loads(get_best_n_players(request, n=1).content.decode())
    best_player_data = best_player[0] if best_player else {}

    best_deck = json.loads(get_best_n_decks(request, n=1).content.decode())
    best_deck_data = best_deck[0] if best_deck else {}

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


def get_best(request):
    _type = request.GET.get("type", None)
    n = int(request.GET.get("n", 1))

    if _type == "deck":
        return get_best_n_decks(request, n)
    elif _type == "player":
        return get_best_n_players(request, n)
    else:
        return JsonResponse({"error": "Invalid Type"}, status=400)


def get_best_n_players(request, n=1):
    players = User.objects.all()
    sorted_players = sorted(players, key=lambda p: (p.win_ratio(), p.total_played()), reverse=True)
    best_n_players = sorted_players[:n]

    return JsonResponse([best.serialize() for best in best_n_players], safe=False)


@login_required
def get_best_n_decks(request, n=5, user_id=None):
    decks = Deck.objects.filter(user=user_id) if user_id else Deck.objects.all()
    sorted_decks = sorted(decks, key=lambda deck: (deck.win_ratio(), deck.total_matches_count), reverse=True)
    best_decks = sorted_decks[:n]

    return JsonResponse([best.serialize() for best in best_decks],safe=False)


@login_required
def get_options(request, _type="result"):
    if _type == "result":
        decks = get_decks_by_user(request=request, user_id=request.user.id)
        decks_decoded = json.loads(decks.content.decode())
        user_decks, rival_decks = decks_decoded["decks"], decks_decoded["no_user_decks"]

        # Format Match.Result.choices for JSON response
        results_match = [{"id": choice[0], "label": choice[1]} for choice in Match.Result.choices]

        return JsonResponse({
            "decks": user_decks,
            "rival_decks": rival_decks,
            "results_match": results_match,
        }, safe=False)

    elif _type == "deck":
        category = [{"id": choice[0], "label": choice[1]} for choice in Deck.Category.choices]
        return JsonResponse({"category": category}, safe=False)

    else:
        return JsonResponse({"error": "Invalid Type"}, status=400)


@login_required()
def add_match(request):
    if request.method == "POST":
        deck1_id = request.POST["deck1"]
        result_code = request.POST["result"]
        deck2_id = request.POST["deck2"]

        print(deck1_id, result_code, deck2_id)

        # Validate required fields
        if not all([deck1_id, deck2_id, result_code]):
            return JsonResponse({"error": "All fields are required."}, status=400)

        # Fetch Deck objects and ensure they are valid
        deck1 = get_object_or_404(Deck, id=deck1_id)
        deck2 = get_object_or_404(Deck, id=deck2_id)

        new_match = Match.objects.create(deck1=deck1, deck2=deck2, result=result_code)
        new_match.save()
        return JsonResponse({"message": "Match added successfully", "match_id": new_match.id})


@login_required
def add_deck(request):
    if request.method == "POST":
        deck_name = request.POST["name"]
        category = request.POST["category"]

        print(deck_name, category)

        if not all([deck_name, category]):
            return JsonResponse({"error": "All fields are required."}, status=400)

        new_deck = Deck.objects.create(user=request.user, name=deck_name, category=category)
        new_deck.save()

        return JsonResponse({"message": "Deck added successfully", "deck_id": new_deck.id})
