# this file is the custom monte carlo framework for our AI to plug into

import numpy as np
import pandas as pd
from random import randint
import importlib
import sys
from icecream import ic
import multiprocessing as mp
import time
from datetime import datetime

from engine.monte_carlo_engine import MonteCarloEngine
from games_config import GAMES_MAP
from games.base_game_object import BaseGameObject


class GameEngine:
    def __init__(self, game_name, sims=100, player_count: int = 2, verbose: bool = False, decay: str = None):
        self.number_of_sims = sims
        self.verbose = verbose
        self.game_name = GAMES_MAP[game_name]
        self.player_count = player_count
        self.game = self.load_game_engine(game_name)
        self.turn = 0  # Set the initial turn as 0
        self.decay = decay
        self.montecarlo = MonteCarloEngine(
            start_player=self.game.get_current_player, verbose=self.verbose
        )  # initialize the monte carlo engine
        self.deep_game_log = []

    def load_game_engine(self, game_name: str) -> BaseGameObject:
        game_module = importlib.import_module(f".{game_name}", package="games")
        game_instance = getattr(game_module, self.game_name)
        return game_instance(self.player_count)

    def play_game_by_turns(self, sims) -> None:
        """
        Intializes Monte Carlo engine
        Will play a single game until game over condition is met

        Available game method hooks:
        self.game.get_current_player() -> int
        self.game.update_game_with_action(action from list, player int)
        self.game.is_game_over() -> bool
        self.game.get_game_scores() -> dict
        self.game.draw_board()
        """

        current_node = self.montecarlo.root  # set first node as monte carlo root
        start_time = time.time()

        while not self.game.is_game_over():
            self.turn += 1  # increments the game turn
            current_player = self.game.get_current_player

            print(f"\n\nTurn {self.turn}\nGame gets {sims} simulations for this turn. Player {current_player}'s turn.")

            current_node, chosen_action, deep_game_log = self.montecarlo.select_and_return_best_real_action(
                num_sims=sims,
                game=self.game,
                node_player=current_player,
                parent=current_node,
            )

            self.deep_game_log += deep_game_log

            self.game.update_game_with_action(action=chosen_action, player=current_player)

            sims = self.update_num_of_sims_for_turn(sims)

            self.game.draw_board()

        print(f"Total time: {time.time()-start_time}\n{self.game.get_game_scores()}")

        pd.DataFrame(self.deep_game_log).to_csv(
            f"logs/{self.game_name}_deep_log_{self.number_of_sims}_sims_games_{datetime.now().strftime('%m%d%Y_%H%M%S')}.csv",
            index=False,
        )

    def update_num_of_sims_for_turn(self, sims):
        if self.decay:
            if self.decay == "halving":
                return int(np.ceil(sims / 2))  # simulation decay halves # sims each round
            if self.decay == "90th":
                return int(np.ceil(sims * 0.9))  # simulation decay of .9 each round
            if self.decay == "div_by_turn":
                return int(
                    np.ceil(self.number_of_sims / (self.turn))
                )  # simulation decay to absolute simulations/turn each round
        return sims
