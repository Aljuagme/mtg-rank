def rank_players(players):
    """Ranks players based on points and match wins."""
    return sorted(players, key=lambda player: (player.points, player.match_wins, player.get_kill_death_ratio()), reverse=True)

def update_player_stats(player, result, is_player1):
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