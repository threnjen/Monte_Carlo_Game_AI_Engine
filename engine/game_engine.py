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
from engine.monte_carlo_node import MonteCarloNode
from games.games_config import GAMES_MAP
from games.base_game_object import BaseGameObject
from itertools import repeat


class GameEngine:
    def __init__(
        self,
        game_name,
        sims=100,
        player_count: int = 2,
        verbose: bool = False,
        decay: str = None,
    ):
        self.number_of_sims = sims
        self.verbose = verbose
        self.game_name = GAMES_MAP[game_name]
        self.player_count = player_count
        self.game = self.load_game_engine(game_name)
        self.turn = 0  # Set the initial turn as 0
        self.decay = decay
        self.game_log = []
        self.montecarlo = MonteCarloEngine(
            start_player=self.get_current_player(), verbose=self.verbose
        )  # initialize the monte carlo engine
        self.deep_game_log = []

    def load_game_engine(self, game_name: str) -> BaseGameObject:
        game_module = importlib.import_module(f".{game_name}", package="games")
        game_instance = getattr(game_module, self.game_name)
        return game_instance(self.player_count)

    def get_current_player(self) -> int:
        """
        Get active player

        Returns:
            int: active player ID
        """
        current_player = self.game.get_current_player()
        return current_player

    def get_available_actions(self, special_policy: bool = False) -> list:
        """
        Get currently available actions

        Returns:
            [list]: List of: list of legal actions
        """
        legal_actions = self.game.get_available_actions(special_policy)
        return legal_actions

    def update_game_with_action(
        self, action_to_record: str, current_player: int
    ) -> None:
        """
        Sends action choice and player to game

        Args:
            action (list item): selected item from list of legal actions
            player (int): player number
        """
        return self.game.update_game_with_action(action_to_record, current_player)

    def is_game_over(self) -> bool:
        """
        Checks if game has ended

        Returns:
            [True/False]: True/False if game is over
        """
        return self.game.is_game_over()

    def get_game_scores(self) -> dict:
        """
        Retrieves game score

        Returns:
            [dict]: dictionary in format playerID: score
        """
        return self.game.get_game_scores()

    def draw_board(self) -> None:
        """
        Requests the game client draw a text representation of the game state
        """
        return self.game.draw_board()

    def _update_turn_log(self, action_to_record, current_player, sims_this_turn):
        self.turn_log["Turn"] = self.turn
        # self.turn_log["Simulations"] = sims_this_turn
        self.turn_log["Player"] = current_player
        self.turn_log["Action"] = str(action_to_record)
        scores = self.get_game_scores()
        # self.turn_log["Score"] = scores[current_player]
        self.game_log.append(self.turn_log)

    def play_game_by_turns(self, sims) -> None:
        """
        Intializes Monte Carlo engine
        Will play a single game until game over condition is met
        """

        current_node = self.montecarlo.root  # set first node as monte carlo root

        while not self.is_game_over():
            sims_this_turn = sims
            self.turn_log = {}
            self.turn += 1  # increments the game turn
            current_player = self.get_current_player()

            print(
                f"\nTurn {self.turn}\nGame gets {sims_this_turn} simulations for this turn. Player {current_player}'s turn."
            )

            current_node, chosen_action, deep_game_log = self.montecarlo.sim_turn_select_best_node(
                num_sims=sims_this_turn,
                game=self.game,
                node_player=current_player,
                parent=current_node,
            )

            self.deep_game_log += deep_game_log

            self.update_game_with_action(chosen_action, current_player)
            self._update_turn_log(
                chosen_action, current_player, sims_this_turn
            )

            sims = self.update_sims(sims)

            print(self.draw_board())

        print(self.get_game_scores())
        # self.montecarlo.tree.draw_graph()
        game_log = pd.DataFrame(self.deep_game_log)

        timestamp = datetime.now().strftime("%m%d%Y_%H%M%S")
        game_log.to_csv(
            f"logs/{self.game_name}_deep_log_{self.number_of_sims}_sims_games_{timestamp}.csv",
            index=False,
        )

    def update_sims(self, sims):
        sims = sims
        if self.decay:
            if self.decay == "halving":
                return int(
                    np.ceil(sims / 2)
                )  # simulation decay halves # sims each round
            if self.decay == "90th":
                return int(np.ceil(sims * 0.9))  # simulation decay of .9 each round
            if self.decay == "div_by_turn":
                return int(
                    np.ceil(self.number_of_sims / (self.turn))
                )  # simulation decay to absolute simulations/turn each round
        return sims


class GameMultiprocessor:
    def __init__(self, game_name, sims, player_count, verbose, num_games, decay):
        self.game_name = game_name
        self.sims = sims
        self.player_count = player_count
        self.verbose = verbose
        self.num_games = num_games
        self.decay = decay
        self.timestamp = datetime.now().strftime("%m%d%Y_%H%M%S")

    def playout_simulations(self):

        time_start = time.time()

        pools = mp.cpu_count()
        print(f"Number of cpu cores available: {pools}")
        processes = 32
        print(f"Number of processes: {processes}")
        self.end = self.num_games
        self.block = int(np.ceil(self.end / processes))
        self.values = np.arange(0, self.end, self.block)
        pool = mp.Pool(processes=processes)
        scores = pool.starmap(
            GameMultiprocessor.process_block, zip(repeat(self), self.values)
        )
        pool.close()
        time_end = round(time.time() - time_start, 3)
        time_per_game = round(time_end / self.num_games, 2)
        print(
            f"Series took {time_end} seconds for {self.num_games} games with {self.sims} simulations each. Average {time_per_game} per game."
        )

        all_games = []
        for game_set in scores:
            for game, data in game_set.items():
                this_game = {}
                this_game["Game"] = game
                for key, value in data["scores"].items():
                    this_game[f"Player {key}"] = value
                for item in data["turn_log"]:
                    this_game[f"T{item['Turn']} P{item['Player']}"] = item["Action"]

                all_games.append(this_game)

        master_game_log = pd.DataFrame(all_games)
        master_game_log[f"starting_sims"] = self.sims
        master_game_log[f"decay_method"] = self.decay
        master_game_log[f"game_time"] = time_per_game

        master_game_log.to_csv(
            f"logs/{self.game_name}_turn_log_{self.sims}_sims_{self.num_games}_games_{self.decay}_{self.timestamp}.csv",
            index=False,
        )

    def process_block(self, values):

        block_games = {}

        end = values + self.block

        if end > self.num_games:
            end = self.num_games

        for games in range(values, end):
            block_games[str(games)] = {}
            game = GameEngine(
                game_name=self.game_name,
                sims=self.sims,
                player_count=self.player_count,
                verbose=self.verbose,
                decay=self.decay,
            )
            game.play_game_by_turns(self.sims)

            block_games[str(games)]["scores"] = game.get_game_scores()
            block_games[str(games)]["turn_log"] = game.game_log

        return block_games
