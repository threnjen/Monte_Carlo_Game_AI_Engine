from random import choice

from pandas import array
from games.base_game_object import GameEnvironment


class TicTacToe(GameEnvironment):
    """Tic tac toe game"""

    def __init__(self, player_count=2):
        """Calling the game doesn't create any unique starting conditions,
        since there are always two player_count.
        """
        self.positions = [" "] * 9
        # self.legal_actions = {}
        self.player_marks = {0: "X", 1: "O"}
        self.scores = {0: 0, 1: 0}
        self.game_over = False
        self.current_player_num = 0
        self.board = ""

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

    def get_game_state(self) -> tuple:
        return (
            tuple(self.positions),
            tuple(self.scores.values()),
            (self.game_over),
            (self.current_player_num),
        )

    def update_game_state(self, game_state: tuple):
        (
            self.positions,
            temp_scores,
            self.game_over,
            self.current_player_num,
        ) = game_state
        self.positions = list(self.positions)
        self.scores.update(zip(self.scores.keys(), temp_scores))

    def draw_board(self):
        """Just draw an ASCII board."""
        self.board = f"""\n
        {self.positions[0]}|{self.positions[1]}|{self.positions[2]}       
        _____
        {self.positions[3]}|{self.positions[4]}|{self.positions[5]}
        _____
        {self.positions[6]}|{self.positions[7]}|{self.positions[8]}"""

        return self.board

    def make_move(self, pos: int, current_player_num: int):
        """Makes a move on the board and draws it"""
        self.positions[pos] = self.player_marks[current_player_num]
        # self.draw_board()
        self.current_player_num = (self.current_player_num + 1) % self.player_count

    def get_current_player(self) -> int:
        return self.current_player_num

    def get_available_actions(self, special_policy: bool = False) -> list:
        """Gets available moves in a dictionary.
        The bot will only ever need the keys; values should be unknown
        """
        legal_actions = [
            pos for pos in range(len(self.positions)) if self.positions[pos] == " "
        ]
        # print(f"Original legal actions: {legal_actions}")

        if special_policy:
            special_policy_actions = []
            current_player = self.get_current_player()
            for win_condition in self.win_conditions.values():
                condition_state = self.get_condition_state(win_condition)

                if (
                    " " in condition_state
                    and condition_state.count(self.player_marks[current_player]) == 2
                ):
                    win_condition = [
                        x for x in win_condition if self.positions[x] == " "
                    ]
                    special_policy_actions += win_condition

            special_policy_actions = list(set(special_policy_actions))
            if len(special_policy_actions) > 0:

                # print(
                #    f"Available win positions for {self.player_marks[current_player]}, Special policy legal actions: {special_policy_actions}"
                # )
                return special_policy_actions

        return legal_actions

    def update_game_with_action(self, action, player):
        self.make_move(action, player)

    def get_condition_state(self, win_condition):
        return [self.positions[num] for num in win_condition]

    def is_game_over(self):
        """Checks for the eight win conditions, and whether there are moves left.

        Returns:
            bool: Over or not
        """

        for win_condition in self.win_conditions.values():
            condition_state = self.get_condition_state(win_condition)

            if (
                condition_state.count(condition_state[0]) == len(condition_state)
                and condition_state[0] != " "
            ):
                open_positions = sum(x == " " for x in self.positions)
                if self.player_marks[0] == condition_state[0]:
                    self.scores[0] = 1
                    self.scores[1] = -1  # - 10*open_positions
                elif self.player_marks[1] == condition_state[0]:
                    self.scores[1] = 1
                    self.scores[0] = -1  # - 10*open_positions
                return True

        avail_actions = self.get_available_actions()

        if len(avail_actions) == 0:
            self.scores[1] = 0
            self.scores[0] = 0

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
            print(f"{self.player_count[player_num]}:  {self.scores[player_num]}")

        return self.scores
