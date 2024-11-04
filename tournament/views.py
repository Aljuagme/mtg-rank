import random

from django.urls import reverse

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

from .forms import ListPlayersForm

from mtg.models import User
from .models import Player, TournamentMatch


# Create your views here.
def setup(request):
    if request.method == 'GET':
        num_players = 8

        # Not working yet =======================================================
        # Pre-fill form fields with user names
        users = User.objects.values_list('username', flat=True)[:num_players]

        initial_data = {f'player_{i + 1}': user for i, user in enumerate(users)}
        print(initial_data)

        # =======================================================================

        # Pass initial data to the form
        form = ListPlayersForm(initial=initial_data)

    elif request.method == 'POST':
        form = ListPlayersForm(request.POST)

        if form.is_valid():
            form_cleaned = form.cleaned_data
            player_names = [name.capitalize() for _, name in form_cleaned.items() if name]

            enroll_participants(player_names)

            return HttpResponseRedirect(reverse('tournament:start'))

    return render(request, "tournament/setup.html", {"form": form})


def enroll_participants(player_names):
    existing_players = Player.objects.filter(name__in=player_names)
    existing_players_names = {player.name for player in existing_players}

    for player in existing_players:
        player.activate()

    new_players = set(player_names) - existing_players_names

    Player.objects.bulk_create([Player(name=name) for name in new_players])

    Player.objects.exclude(name__in=player_names).update(active=False)


@login_required
def start(request):
    return render(request, "tournament/start.html")






@login_required
def get_players(request):
    players = Player.objects.filter(active=True)

    players_data = [player.serialize() for player in players]
    random.shuffle(players_data)

    return JsonResponse(players_data, safe=False)
