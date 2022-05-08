import sys
from engine.game_engine import GameEngine
import argparse

def parseArguments():
    # Create argument parser
    parser = argparse.ArgumentParser()

    # Positional mandatory arguments
    parser.add_argument("game", help="Game name", type=str)

    # Optional arguments
    parser.add_argument("-s", help="Number of simulations", type=int, default=1000)
    parser.add_argument("-p", help="Number of players", type=int, default=2)
    parser.add_argument("-v", help="Verbosity", type=bool, default=False)

    # Parse arguments
    args = parser.parse_args()

    return args

if __name__ == "__main__":
    '''
    game = game name (required)
    -s = # of simulations (default 1000)
    -p = # of players (default 2)
    -v = verbosity (default False)
    '''
    
    # Parse the arguments
    args = parseArguments()
    
    game = args.__dict__['game']
    sims = args.__dict__['s']
    players = args.__dict__['p']
    verbose = args.__dict__['v']

    print(f"Initializing game: {game}, # sims: {sims}, # players: {players}, verbose: {verbose}")

    #game = GameEngine(game, players, verbose)
    #game.play_game_byturns(sims)