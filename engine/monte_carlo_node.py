from __future__ import annotations
import numpy as np

class MonteCarloNode():
    def __init__(
        self, label="Root Node", depth=0, player=None, game_state: tuple = None, game_image: str = None
    ):  # , legal_actions=None
        """
        Initializes monte carlo node

        Args:
            parent (object instance, optional): Node object that spawned this node. Defaults to None.
            node_action (int or str, optional): Action this node returns to game state when node is activated. Defaults to None.
            label (str, optional): Node label for GUI reporting. Defaults to 'Root Node'.
            depth (int, optional): Depth of node in tree. Defaults to 0.
            player (int, optional): Player ID of node owner. Defaults to None.
        """

        self._number_of_visits = 0  # number of times current node is visited
        self._total_score = 0  # total score for this node ONLY for its owner
        self._label = label  # label for the node, is used in GUI reporting
        self._depth = depth  # depth of the node
        self._player_owner = player  # the player who owns/plays this node layer. Should be same player at any given depth.
        self._game_state = game_state
        self._game_image = game_image

    def add_to_visits(self, visits_to_add: int):
        self._number_of_visits += visits_to_add

    def get_node_owner(self):
        return self._player_owner

    def add_to_score(self, points_to_add: float):
        self._total_score += points_to_add

    def get_total_score(self) -> float:
        return self._total_score

    def get_depth(self) -> int:
        return self._depth

    def get_visit_count(self) -> int:
        return self._number_of_visits

    def get_game_state(self) -> tuple:
        return self._game_state

    def get_game_image(self) -> str:
        return self._game_image
