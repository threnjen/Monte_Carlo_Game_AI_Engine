import sys
from engine.game_engine import GameEngine
import argparse

def parseArguments():
    # Create argument parser
    parser = argparse.ArgumentParser()

    # Positional mandatory arguments
    parser.add_argument("game", help="Game name", type=str)

    # Optional arguments
    parser.add_argument("-s", help="Number of simulations", type=int, default=100)
    parser.add_argument("-p", help="Number of player_count", type=int, default=2)
    parser.add_argument("-v", help="Verbosity", type=bool, default=False)

    # Parse arguments
    args = parser.parse_args()

    return args

if __name__ == "__main__":
    '''
    game_name = game name (required)
    -s = # of simulations (default 1000)
    -p = # of player_count (default 2)
    -v = verbosity (default False)
    '''
    
    # Parse the arguments
    args = parseArguments()
    
    game_name = args.__dict__['game']
    sims = args.__dict__['s']
    player_count = args.__dict__['p']
    verbose = args.__dict__['v']

    print(f"Initializing game: {game_name}, # sims: {sims}, # player_count: {player_count}, verbose: {verbose}")

    game = GameEngine(game_name, sims, player_count, verbose)
    game.play_game_byturns()