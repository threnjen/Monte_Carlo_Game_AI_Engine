import pytest

from engine.game_engine import GameEngine


@pytest.fixture()
def engine():
    game_name = 'simple_array_game'
    sims = 1000
    players = 3
    verbose = True

    engine = GameEngine(game_name, sims, players, verbose)
    return engine