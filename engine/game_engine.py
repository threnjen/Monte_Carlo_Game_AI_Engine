# this file is the custom monte carlo framework for our AI to plug into

import numpy as np
import pandas as pd
from random import randint
import importlib
import sys

from engine.monte_carlo_engine import MonteCarloEngine
from engine.monte_carlo_node import MonteCarloNode
from games.games_config import GAMES_MAP
from games.base_game_object import BaseGameObject


class GameEngine:
    def __init__(self, game, player_count: int = 2, verbose: bool = False):
        self.verbose = verbose
        self.game_name = GAMES_MAP[game]
        self.player_count = player_count
        self.game = self.load_game_engine(game)
        self.turn = 0  # Set the initial turn as 0
        self.game_log = []
        self.montecarlo = MonteCarloEngine(
            start_player=self.get_current_player(), verbose=self.verbose
        )  # initialize the monte carlo engine

    def load_game_engine(self, game: str) -> BaseGameObject:
        game_module = importlib.import_module(f".{game}", package="games")
        game_instance = getattr(game_module, self.game_name)
        return game_instance(self.player_count)

    def get_current_player(self) -> list[int]:
        """
        Get active player

        Returns:
            [list]: active player ID
        """
        current_player = self.game.get_current_player()
        return current_player

    def get_available_actions(self, special_policy=False) -> list:
        """
        Get currently available actions

        Returns:
            [list]: List of: list of legal actions
        """
        legal_actions = self.game.get_available_actions(special_policy)
        return legal_actions

    def is_game_over(self) -> bool:
        """
        Checks if game has ended

        Returns:
            [True/False]: True/False if game is over
        """
        return self.game.is_game_over()

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

    def _update_game_log(
        self, action_to_record, current_player, sims_this_turn
    ):  # TO DO make this a dict update not a pandas append
        self.turn_log["Turn"] = self.turn
        self.turn_log["Simulations"] = sims_this_turn
        self.turn_log["Player"] = current_player
        self.turn_log["Action"] = str(action_to_record)
        scores = self.get_game_scores()
        self.turn_log["Score"] = scores[current_player]
        self.game_log.append(self.turn_log)

    def _get_best_move_node(
        self, sims_this_turn: int, current_player: int, incoming_node: MonteCarloNode
    ) -> MonteCarloNode:
        return self.montecarlo.sim_turn_select_best_node(
            num_sims=sims_this_turn,
            game=self.game,
            node_player=current_player,
            incoming_node=incoming_node,
        )

    def _get_best_node_action(self, current_node: MonteCarloNode) -> str:
        node_action = self.montecarlo.get_node_action(
            current_node
        )  # gets action of the returned node
        print("Move: " + str(node_action))
        return node_action

    def play_game_by_turns(
        self,
        sims: int = 100,
    ) -> None:
        """
        Intializes Monte Carlo engine
        Will play a single game until game over condition is met
        """
        # if self.verbose:
        # sys.stdout = open(f'logs/{self.name}_{self.player_count}player_count_{self.simulations}sims_{randint(1,1000000)}.txt', "w")
        print(f"player_count: {self.player_count}, Sims: {sims}")

        current_node = self.montecarlo.root  # set first node as monte carlo root

        while not self.is_game_over():
            sims_this_turn = sims
            self.turn_log = {}
            self.turn += 1  # increments the game turn
            actions = self.get_available_actions()
            self.turn_log["Actions"] = actions
            current_player = self.get_current_player()

            print(
                f"\n\nTurn {self.turn}\nGame gets {sims_this_turn} simulations for this turn. Player {current_player}'s turn."
            )

            if self.verbose:
                try:
                    print(
                        f"Entry state {current_node.depth}, {self.montecarlo.get_node_action()}, {current_node.player_owner}, {current_node}"
                    )
                except:
                    pass

            current_node = self._get_best_move_node(
                sims_this_turn=sims_this_turn,
                current_player=current_player,
                incoming_node=current_node,
            )

            action_to_record = self._get_best_node_action(current_node)
            self.update_game_with_action(action_to_record, current_player)
            self._update_game_log(action_to_record, current_player, sims_this_turn)

            # Add simulation decay if desired. Uncomment choices below for two types of simulation decay.

            # simulation decay of .9 each round
            # sims = int(np.ceil(sims * 0.9))
            # sims = int(np.ceil(sims/(self.turn))) # simulation decay to absolute simulations/turn each round

        # Game over report
        print(
            f"\n\n\nGame over. Game took {self.turn} turns.\n{self.draw_board()}\n{self.get_game_scores()}"
        )

        # if self.verbose:
        # sys.stdout.close()

        game_log = pd.DataFrame(self.game_log).to_csv(
            "logs/" + self.game_name + "_game_log_" + str(randint(1, 1000000)) + ".pkl"
        )

        # first_action_list=[]

        # for i in range(self.simulations):

        #    self.action = self.turn_engine.sim_turn_select_best_node(1, self.game, self.player)
        #    first_action_list.append(tuple(self.action))

        # df = pd.DataFrame(first_action_list)
        # df['pairs'] = df.apply(lambda x: (str(x[0])+", "+str(x[1])), axis=1)
        # df.to_pickle('first_action_list'+str(game_label)+'.pkl')
