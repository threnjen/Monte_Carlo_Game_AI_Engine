from engine.game_engine import GameEngine
#import games.azul
import importlib

def test_engine():
    
    game_name = 'tic_tac_toe'
    sims = 1000
    players = 3
    verbose = True

    game = GameEngine(game_name, sims, players, verbose)

    assert game.simulations==1000
    assert game.player_count==3
    assert game.verbose==True

def test_legal_actions():
    pass

def test_game_over():
    pass

def test_update_game():
    pass

def test_game_result():
    pass
