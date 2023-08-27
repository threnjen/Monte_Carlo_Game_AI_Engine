# import numpy as np
from copy import copy, deepcopy
from collections import defaultdict
from itertools import product
from games.base_game_object import BaseGameObject


class SimpleArrayGame(BaseGameObject):
    """
    Game rules:
    There is an array of 5x5 zeros
    Each round, the player puts a 1 in a specific slot of the array
    When any column sums to 5, the game is over
    The score is the index of the column that was filled

    """

    def __init__(self, player_count):
        # self.board = np.zeros((5, 5))
        self.board = [[0 for x in range(0, 5)] for x in range(0, 5)]
        self.name = "array_test"
        self.positions = [x for x in product(list(range(0, 5)), list(range(0, 5)))]

    def get_available_actions(self, special_policy: bool = False) -> list:
        # return list([tuple(i) for i in (np.argwhere(self.board == 0))])
        return [(i, y) for i in range(len(self.board)) for y in range(len(self.board[i])) if self.board[i][y] == 0]

    def get_current_player(self) -> int:
        return 0

    def is_game_over(self):
        # return np.any(self.board.sum(axis=0) == 5)
        column_sums = defaultdict(int)

        for x in self.positions:
            column_sums[x[1]] += self.board[x[0]][x[1]]
            if column_sums[x[1]] == 1:
                return True
        return False

    def update_game_with_action(self, action, player):
        # self.board[action] = 1
        self.board[action[0]][action[1]] = 1
        return self.board

    def get_game_scores(self):
        scores = {}
        column_sums = defaultdict(int)

        for x in self.positions:
            column_sums[x[1]] += self.board[x[0]][x[1]]
            if column_sums[x[1]] == 1:
                scores[0] = x[1]
        # finished_array = self.board.sum(axis=0)
        # scores[0] = np.argmax(finished_array)
        return scores

    def draw_board(self):
        print(self.board)

    def save_game_state(self):
        print("Saving game state.")
        self.save_game = {}
        # self.save_game["board"] = deepcopy(self.board)
        self.save_game["board"] = [[cell for cell in row] for row in self.board]

    def load_save_game_state(self):
        # self.board = deepcopy(self.save_game["board"])
        self.board = [[cell for cell in row] for row in self.save_game["board"]]
