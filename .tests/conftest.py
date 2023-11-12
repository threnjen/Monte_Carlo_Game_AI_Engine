import pytest

from engine.game_engine import GameEngine


@pytest.fixture()
def engine():
    game_name = 'simple_array_game'
    sims = 10
    player_count = 3
    verbose = True

    engine = GameEngine(game_name, sims, player_count, verbose)
    return engine