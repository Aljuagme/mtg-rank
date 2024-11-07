import json
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
    """View to set up tournament players."""
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
            player_names = [name.capitalize() for _, name in form.cleaned_data.items() if name]
            enroll_participants(player_names)
            return HttpResponseRedirect(reverse('tournament:start'))

    return render(request, "tournament/setup.html", {"form": form})


def enroll_participants(player_names):
    """Enrolls or activates players based on provided names."""
    existing_players = Player.objects.filter(name__in=player_names)
    existing_players_names = {player.name for player in existing_players}

    existing_players.update(active=True)
    new_names = set(player_names) - existing_players_names
    Player.objects.bulk_create([Player(name=name) for name in new_names])

    Player.objects.exclude(name__in=player_names).update(active=False)


@login_required
def start(request):
    """Starts the tournament view."""
    return render(request, "tournament/start.html")




@login_required
def play_round(request, n_round):
    """Plays a specified round, creating or retrieving matches as needed."""
    players = get_players(n_round=n_round)
    ranked_players = [player.serialize() for player in rank_players(players)]

    # Check if matches for this round already exist and are active
    matches = TournamentMatch.objects.filter(n_round=n_round, active=True)

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

def update_player_points(player, result, is_player1):
    """
    Updates a player's points, match_wins, and match_losses based on the match result.
    """
    point_mapping = {
        "AW": ((3, 2, 0) if is_player1 else (0, 0, 2)),
        "WN": (3 if is_player1 else 0, 2 if is_player1 else 1, 1 if is_player1 else 2),
        "DW": (1, 1, 1),
        "LS": (0 if is_player1 else 3, 1 if is_player1 else 2, 2 if is_player1 else 1),
        "AL": ((0, 0, 2) if  is_player1 else (3, 2, 0)),
    }

    points, wins, losses = point_mapping.get(result)
    player.points += points
    player.match_wins += wins
    player.match_losses += losses

@login_required
def next_round(request):
    """Processes match results for the current round and updates player data."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            round_number = data.get("roundNumber")
            match_results = data.get("formData")

            players = {p.name: p for p in get_players()}

            for match in match_results:
                player1, player2 = players.get(match["player1Name"]), players.get(match["player2Name"])
                if not player1 or not player2:
                    return JsonResponse({"status": "error", "message": "Player not found in database."}, status=404)

                # Update player stats based on match result
                update_player_points(player1, match["result"], is_player1=True)
                update_player_points(player2, match["result"], is_player1=False)

            for player in players.values():
                player.save()

            return JsonResponse({"status": "success", "message": f"Round {round_number} data processed successfully."})

        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON body."}, status=400)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)



def create_matches(players, n_round):
    """Creates new matches for the round and deactivates previous ones."""
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
    """Retrieves and shuffles active players if it's the first round."""
    players = list(Player.objects.filter(active=True))
    if n_round == 1:
        random.shuffle(players)
    return players



@login_required
def get_possible_results(request):
    """Fetches all possible match results."""
    results_match = [{"id": choice[0], "label": choice[1]} for choice in TournamentMatch.Result.choices]
    return JsonResponse(results_match, safe=False)


def rank_players(players):
    """Ranks players based on points and match wins."""
    return sorted(players,
                  key=lambda player: (player.points, player.match_wins),
                  reverse=True)
