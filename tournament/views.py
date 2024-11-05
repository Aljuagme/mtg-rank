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
        # Pre-fill form fields with usernames
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
def play_round(request, n_round):
    players = get_players(n_round=n_round)
    ranked_players = [player.serialize() for player in rank_players(players)]
    # Check if matches for this round already exist and are active
    matches = TournamentMatch.objects.filter(n_round=n_round, active=True)
    print(f"Existing matches for round {n_round}: {matches}")

    print(matches.exists())

    if not matches.exists():
        create_matches(players, n_round=n_round)
        matches = TournamentMatch.objects.filter(n_round=n_round, active=True)

    match_data = [match.serialize() for match in matches]

    return JsonResponse(
        {
            "match_data": match_data,
            "ranked_players": ranked_players
        },
    safe=False)



def create_matches(players, n_round):
    n_pairs = len(players) // 2

    TournamentMatch.objects.all().update(active=False)
    # TournamentMatch.objects.filter(n_round__lt=n_round).update(active=False) LESS THAN! WOW

    TournamentMatch.objects.bulk_create([
        TournamentMatch(
            player1=players[i],
            player2=players[i + n_pairs],
            n_round=n_round
        )
        for i in range(n_pairs)
    ])


def get_players(n_round=None):
    players = Player.objects.filter(active=True)

    players_data = list(players)

    if n_round == 1:
        random.shuffle(players_data)

    return players_data



@login_required
def get_possible_results(request):
    results_match = [{"id": choice[0], "label": choice[1]} for choice in TournamentMatch.Result.choices]
    return JsonResponse(results_match, safe=False)


def rank_players(players):
    ranked_players = sorted(players, key=lambda player: (player.points, player.match_wins), reverse=True)
    print("Ranked Players: ", ranked_players)
    return ranked_players