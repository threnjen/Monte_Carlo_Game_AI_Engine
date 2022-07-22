import numpy as np
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
        self.board = np.zeros((5, 5))
        self.name = "array_test"

    def get_available_actions(self, special_policy: bool = False) -> list:
        return list([tuple(i) for i in (np.argwhere(self.board == 0))])

    def get_current_player(self) -> int:
        return 0

    def is_game_over(self):
        return np.any(self.board.sum(axis=0) == 5)

    def update_game_with_action(self, action, player):
        # action = tuple(action)
        self.board[action] = 1
        return self.board

    def get_game_scores(self):
        scores = {}
        finished_array = self.board.sum(axis=0)
        scores[0] = np.argmax(finished_array)
        return scores

    def draw_board(self):
        print(self.board)
