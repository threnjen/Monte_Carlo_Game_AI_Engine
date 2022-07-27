# this file is the custom monte carlo framework for our AI to plug into

import numpy as np
import pandas as pd
from random import randint
import importlib
import sys

from engine.monte_carlo_engine import MonteCarloEngine
from games.games_config import GAMES_MAP


class GameEngine:
    def __init__(
        self, game, sims: int = 100, player_count: int = 2, verbose: bool = False
    ):
        self.verbose = verbose
        self.game_name = GAMES_MAP[game]
        game_module = importlib.import_module(f".{game}", package="games")
        game_instance = getattr(game_module, self.game_name)
        self.player_count = player_count
        self.game = game_instance(self.player_count)
        self.simulations = sims
        self.turn = 0  # Set the initial turn as 0
        self.game_log = pd.DataFrame(
            columns=["Turn", "Actions", "Player", "Action", "Score", "Simulations"]
        )
        self.current_player = self.get_current_player()  # Get starting player
        self.montecarlo = MonteCarloEngine(
            start_player=self.current_player, verbose=self.verbose
        )  # initialize the monte carlo engine

    def get_current_player(self):
        """
        Get active player

        Returns:
            [list]: active player ID
        """
        current_player = self.game.get_current_player()
        return current_player

    def get_available_actions(self, policy=False) -> list:
        """
        Get currently available actions

        Returns:
            [list]: List of: list of legal actions
        """
        legal_actions = self.game.get_available_actions(policy)
        return legal_actions

    def is_game_over(self):
        """
        Checks if game has ended

        Returns:
            [True/False]: True/False if game is over
        """
        return self.game.is_game_over()

    def update_game(self):
        """
        Sends action choice and player to game

        Args:
            action (list item): selected item from list of legal actions
            player (int): player number
        """
        return self.game.update_game(self.node_action, self.current_player)

    def game_result(self):
        """
        Retrieves game score

        Returns:
            [dict]: dictionary in format playerID: score
        """
        return self.game.game_result()

    def draw_board(self):
        """
        Requests the game client draw a text representation of the game state

        Returns:
            draws game state
        """

        return self.game.draw_board()

    def _update_game_log(self):
        self.game_log.append(self.turn_log, ignore_index=True)

    def _update_turn_log(self):
        self.turn_log["Turn"] = self.turn
        self.turn_log["Simulations"] = self.sims_this_turn
        self.turn_log["Player"] = self.current_player
        self.turn_log["Action"] = str(self.node_action)
        scores = self.game_result()
        self.turn_log["Score"] = scores[self.current_player]

    def _set_base_node(self):
        return self.montecarlo.root

    def _get_current_node(self):
        current_node = self.montecarlo.play_turn(
            num_sims=self.sims_this_turn,
            game=self.game,
            node_player=self.current_player,
            received_node=self.current_node,
        )
        return current_node

    def _get_node_action(self, current_node):
        node_action = current_node.node_action  # gets action of the returned node
        print("Move: " + str(node_action))
        return node_action

    def play_game_byturns(self):
        """
        Intializes Monte Carlo engine
        Will play a single game until game over condition is met
        """
        # if self.verbose:
        # sys.stdout = open(f'logs/{self.name}_{self.player_count}player_count_{self.simulations}sims_{randint(1,1000000)}.txt', "w")
        print(f"player_count: {self.player_count}, Sims: {self.simulations}")

        self.current_node = self._set_base_node()  # set first node as monte carlo root

        self.sims_this_turn = (
            self.simulations
        )  # set number of simulations; re-assigned here for decay usage

        while not self.is_game_over():

            self.turn_log = {}
            self.turn += 1  # increments the game turn
            actions = self.get_available_actions()
            self.player = self.get_current_player()
            self.turn_log["Actions"] = actions

            print(
                f"\n\nTurn {self.turn}\nGame gets {self.sims_this_turn} simulations for this turn. Player {self.current_player}'s turn."
            )

            if self.verbose:
                try:
                    print(
                        f"Entry state {self.current_node.depth}, {self.current_node.node_action}, {self.current_node.player_owner}, {self.current_node}"
                    )
                except:
                    pass

            current_node = (
                self._get_current_node()
            )  # Run the monte carlo engine for this turn and receive the chosen action node
            self.node_action = self._get_node_action(
                current_node
            )  # check the action of the current node

            self.update_game()  # updates the true game state with the MC simmed action

            self._update_turn_log()  # log individual turn
            self._update_game_log()  # add turn to game log

            # Add simulation decay if desired. Uncomment choices below for two types of simulation decay.
            self.sims_this_turn = int(
                np.ceil(self.sims_this_turn * 0.9)
            )  # simulation decay of .9 each round
            # sims_this_turn = int(np.ceil(self.simulations/(self.turn))) # simulation decay to absolute simulations/turn each round

        # Game over report
        print(
            f"\n\n\nGame over. Game took {self.turn} turns.\n{self.draw_board()}\n{self.game_result()}"
        )

        # if self.verbose:
        # sys.stdout.close()

        self.game_log.to_pickle(
            "logs/" + self.name + "_game_log_" + str(randint(1, 1000000)) + ".pkl"
        )

        # first_action_list=[]

        # for i in range(self.simulations):

        #    self.action = self.turn_engine.play_turn(1, self.game, self.player)
        #    first_action_list.append(tuple(self.action))

        # df = pd.DataFrame(first_action_list)
        # df['pairs'] = df.apply(lambda x: (str(x[0])+", "+str(x[1])), axis=1)
        # df.to_pickle('first_action_list'+str(game_label)+'.pkl')
