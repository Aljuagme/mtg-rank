import json
import random
from json import JSONDecodeError

from .utils import update_player_stats, rank_players
from .forms import ListPlayersForm
from mtg.models import User
from .models import Player, TournamentMatch


def get_players(n_round=None):
    """Retrieves and shuffles active players for the first round."""
    players = list(Player.objects.filter(active=True))
    if n_round == 1:
        random.shuffle(players)
    return players

def get_prefilled_form(num_players=8):
    """Get form pre-filled with initial usernames."""
    users = User.objects.values_list('username', flat=True)[:num_players]
    initial_data = {f'player_{i + 1}': user for i, user in enumerate(users)}
    return ListPlayersForm(initial=initial_data)

def enroll_and_start(player_data):
    """Enrolls participants based on form data and starts the tournament."""
    player_names = [name.capitalize() for name in player_data.values() if name]
    enroll_participants(player_names)

def enroll_participants(player_names):
    """Enrolls or activates players based on provided names."""
    existing_players = Player.objects.filter(name__in=player_names)
    existing_players_names = {player.name for player in existing_players}

    existing_players.update(active=True)
    new_names = set(player_names) - existing_players_names
    Player.objects.bulk_create([Player(name=name) for name in new_names])
    Player.objects.exclude(name__in=player_names).update(active=False)

def create_matches(players, n_round):
    """Creates matches for a new round."""
    n_pairs = len(players) // 2
    TournamentMatch.objects.filter(n_round=n_round).update(active=False)

    matches = [
        TournamentMatch(player1=players[i], player2=players[i + n_pairs], n_round=n_round)
        for i in range(n_pairs)
    ]
    TournamentMatch.objects.bulk_create(matches)

def get_match_results():
    """Fetches all possible match result choices."""
    return [{"id": choice[0], "label": choice[1]} for choice in TournamentMatch.Result.choices]


def process_round_results(request):
    try:
        data = json.loads(request.body)
        round_number = data.get("roundNumber")
        match_results = data.get("formData")

        if not round_number or not match_results:
            return {"status": "error", "message": "Missing round number or formData", "status_code": 400}

        players = {p.name: p for p in get_players()}
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
    players = get_players(n_round)
    ranked_players = [player.serialize() for player in rank_players(players)]
    option_results = get_match_results()

    matches = TournamentMatch.objects.filter(n_round=n_round, active=True)
    if not matches.exists():
        create_matches(players, n_round)
        matches = TournamentMatch.objects.filter(n_round=n_round, active=True)

    match_data = [match.serialize() for match in matches]
    return match_data, ranked_players, option_results