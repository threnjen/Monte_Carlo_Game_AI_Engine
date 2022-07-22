from random import choice

from pandas import array
from games.base_game_object import BaseGameObject


class Player:
    """Player class.  Not much here"""

    def __init__(self, mark, isbot=False):
        """Player class

        Args:
            mark (str): X or O
            isbot (bool, optional): Whether this is a bot. Defaults to False.
        """
        self.mark = mark


class TicTacToe(BaseGameObject):
    """Tic tac toe game"""

    def __init__(self, player_count=2):
        """Calling the game doesn't create any unique starting conditions,
        since there are always two player_count.
        """
        self.positions = [" "] * 9
        # self.legal_actions = {}
        self.player_marks = {0: Player("0"), 1: Player("1")}
        self.scores = {0: 0, 1: 0}
        self.game_over = False
        self.current_player_num = 0
        self.board = ""
        self.draw_board()

        self.win_conditions = {
            "top_row": [0, 1, 2],
            "left_diag": [0, 4, 8],
            "mid_row": [3, 4, 5],
            "bot_row": [6, 7, 8],
            "right_diag": [6, 4, 2],
            "left_col": [0, 3, 6],
            "mid_col": [1, 4, 7],
            "right_col": [2, 5, 8],
        }

        self.player_count = 2

    def draw_board(self):
        """Just draw an ASCII board."""
        self.board = f"""\n
        {self.positions[0]}|{self.positions[1]}|{self.positions[2]}       
        _____
        {self.positions[3]}|{self.positions[4]}|{self.positions[5]}
        _____
        {self.positions[6]}|{self.positions[7]}|{self.positions[8]}"""

        print(self.board)

    def make_move(self, pos: int, current_player_num: int):
        """Makes a move on the board and draws it"""
        self.positions[pos] = self.player_marks[current_player_num].mark
        self.draw_board()
        self.current_player_num = (self.current_player_num + 1) % self.player_count

    def get_current_player(self) -> int:
        return self.current_player_num

    def get_available_actions(self, special_policy=False) -> list:
        """Gets available moves in a dictionary.
        The bot will only ever need the keys; values should be unknown
        """
        legal_actions = []
        for pos in range(len(self.positions)):
            # print(self.positions)
            if self.positions[pos] == " ":
                legal_actions.append(pos)
        return legal_actions

    def update_game_with_action(self, action, player):
        self.make_move(action, player)

    def is_game_over(self):
        """Checks for the eight win conditions, and whether there are moves left.

        Returns:
            bool: Over or not
        """
        avail_actions = self.get_available_actions()

        for win_condition in self.win_conditions.values():

            condition_state = [self.positions[num] for num in win_condition]

            if (
                condition_state.count(condition_state[0]) == len(condition_state)
                and condition_state[0] != " "
            ):
                open_positions = sum(x == " " for x in self.positions)
                if self.player_marks[0].mark == condition_state[0]:
                    self.scores[0] = 10
                    self.scores[1] = -10  # - 10*open_positions
                elif self.player_marks[1].mark == condition_state[0]:
                    self.scores[1] = 10
                    self.scores[0] = -10  # - 10*open_positions
                return True

        if len(avail_actions) == 0:

            return True
        else:
            return False

    def get_game_scores(self):
        return self.scores

    def play_game(self):
        while not self.is_game_over():
            pos = int(input("Select a move.  "))
            self.make_move(pos, self.current_player_num)

        for player_num in self.scores.keys():
            print(f"{self.player_count[player_num].mark}:  {self.scores[player_num]}")

        return self.scores
