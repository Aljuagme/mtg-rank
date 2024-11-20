import json
import random
from json import JSONDecodeError

from .utils import update_player_stats, rank_players
from .forms import ListPlayersForm
from mtg.models import User
from .models import Player, TournamentMatch, Tournament, PlayerTournamentStats


def get_players(tournament, n_round=None):
    """Retrieves and shuffles active players for the first round."""
    players = list(PlayerTournamentStats.objects.filter(active=True, tournament=tournament))
    if n_round == 1:
        random.shuffle(players)
    return players

def get_prefilled_form(num_players=8):
    """Get form pre-filled with initial usernames."""
    users = User.objects.values_list('username', flat=True)[:num_players]
    initial_data = {f'player_{i + 1}': user for i, user in enumerate(users)}
    return ListPlayersForm(initial=initial_data)

def enroll_players(player_data):
    """Enrolls participants based on form data and starts the tournament."""
    player_names = [name.capitalize() for name in player_data.values() if name]
    tournament = get_or_create_tournament()

    for name in player_names:
        player, _ = Player.objects.get_or_create(name=name)
        stats, created = PlayerTournamentStats.objects.get_or_create(player=player, tournament=tournament)
        if not created:
            stats.reset_stats()
        stats.active = True
        stats.save()

    PlayerTournamentStats.objects.filter(tournament=tournament).exclude(player__name__in=player_names).update(active=False)


def create_matches(players, n_round, tournament):
    """Creates matches for a new round."""
    pairs = []
    paired = [False] * len(players)
    ranked_players = rank_players(players)

    while False in paired:
        for i, r_player in enumerate(ranked_players):
            if paired[i]:
                continue
            for j in range(i + 1, len(ranked_players)):
                if not paired[j] and paired[j] not in r_player.get_rivals(tournament):
                    pairs.append((r_player, ranked_players[j]))
                    paired[i] = paired[j] = True
                    break

    matches = [
        TournamentMatch(player1=pairs[i][0], player2=pairs[i][1], n_round=n_round, tournament=tournament)
        for i in range(len(pairs))
    ]
    TournamentMatch.objects.bulk_create(matches)


def get_match_results():
    """Fetches all possible match result choices."""
    return [{"id": choice[0], "label": choice[1]} for choice in TournamentMatch.Result.choices]


def process_round_results(request):
    tournament = get_or_create_tournament()
    try:
        data = json.loads(request.body)
        round_number = data.get("roundNumber")
        match_results = data.get("formData")

        if not round_number or not match_results:
            return {"status": "error", "message": "Missing round number or formData", "status_code": 400}

        players = {p.player.name: p for p in get_players(tournament)}
        for match in match_results:
            player1 = players.get(match["player1Name"])
            player2 = players.get(match["player2Name"])
            if not player1 or not player2:
                return {"status": "error", "message": "Missing player1 or player2 name", "status_code": 400}

            update_player_stats(player1, match["result"], is_player1=True)
            update_player_stats(player2, match["result"], is_player1=False)

        for player in players.values():
            player.save()

        return {"status": "success", "message": f"Round {round_number} processed successfully"}
    except JSONDecodeError:
        return {"status": "error", "message": "Invalid JSON Body", "status_code": 400}

def get_round_data(n_round):
    tournament = get_or_create_tournament()
    players = get_players(tournament, n_round)
    ranked_players = [player.serialize() for player in rank_players(players)]
    option_results = get_match_results()

    matches = TournamentMatch.objects.filter(n_round=n_round, tournament=tournament, active=True)
    if not matches.exists():
        create_matches(players, n_round, tournament)
        matches = TournamentMatch.objects.filter(n_round=n_round, tournament=tournament, active=True)


    match_data = [match.serialize() for match in matches]
    return match_data, ranked_players, option_results


def get_or_create_tournament(setup=False):
    """Fetches the active tournament or creates one if none exists."""
    if setup:
        Tournament.objects.filter(active=True).update(active=False)
    tournament, created = Tournament.objects.get_or_create(active=True)
    return tournament

def end_tournament():
    """Deactivates the active tournament."""
    Tournament.objects.filter(active=True).update(active=False)