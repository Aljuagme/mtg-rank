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
    return JsonResponse([deck.serialize() for deck in decks], safe=False)

@login_required
def get_results(request):
    matchs = Match.objects.all()
    return JsonResponse([match.serialize() for match in matchs], safe=False)

@login_required
def get_results_by_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    matchs = Match.objects.filter(user=user)
    return JsonResponse([match.serialize() for match in matchs], safe=False)