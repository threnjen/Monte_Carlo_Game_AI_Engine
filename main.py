import sys
from engine.game_multiprocessor import GameMultiprocessor
from engine.game_engine import GameEngine
import argparse
from icecream import install

install()


def parseArguments():
    # Create argument parser
    parser = argparse.ArgumentParser()

    # Positional mandatory arguments
    parser.add_argument("game", help="Game name", type=str)

    # Optional arguments
    parser.add_argument("-s", help="Number of simulations", type=int, default=100)
    parser.add_argument("-p", help="Number of player_count", type=int, default=2)
    parser.add_argument("-v", help="Verbosity", type=bool, default=False)
    parser.add_argument("-g", help="number of games to play", type=int, default=1)
    parser.add_argument(
        "-d",
        help="simulation decay method [halving, 90th, div_by_turn]",
        type=str,
        default="no_decay",
    )

    # Parse arguments
    args = parser.parse_args()

    return args


if __name__ == "__main__":
    """
    game_name = game name (required)
    -s = # of simulations (default 1000)
    -p = # of player_count (default 2)
    -v = verbosity (default False)
    -g = games (default 1)
    -d = sim decay (default none)
    """

    # Parse the arguments
    args = parseArguments()

    game_name = args.__dict__["game"]
    sims = args.__dict__["s"]
    player_count = args.__dict__["p"]
    verbose = args.__dict__["v"]
    num_games = args.__dict__["g"]
    decay = args.__dict__["d"]

    print(
        f"Initializing game: {game_name}, # sims: {sims}, # player_count: {player_count}, verbose: {verbose}, num_games: {num_games}, decay: {decay}"
    )

    GameMultiprocessor(game_name, sims, player_count, verbose, num_games, decay).playout_simulations()
