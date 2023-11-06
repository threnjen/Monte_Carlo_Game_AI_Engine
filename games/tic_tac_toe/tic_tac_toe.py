from typing import Any

from games.game_components.base_game_object import BaseGameObject
from .player import TicTacToePlayer
from typing import ClassVar
from .action import TicTacToeAction
import numpy as np
from pydantic import Field


class TicTacToe(BaseGameObject):
    """Tic tac toe game"""

    empty_space: ClassVar[int] = -1
    player_count: int = 2
    positions: list[int] = Field(
        default_factory=lambda: [TicTacToe.empty_space]
        * TicTacToeAction.ACTION_SPACE_SIZE
    )
    current_player_num: int = 0
    win_conditions: ClassVar[dict[str, np.ndarray[int]]] = {
        "top_row": np.array([0, 1, 2]),
        "mid_row": np.array([3, 4, 5]),
        "bot_row": np.array([6, 7, 8]),
        "left_col": np.array([0, 3, 6]),
        "mid_col": np.array([1, 4, 7]),
        "right_col": np.array([2, 5, 8]),
        "left_diag": np.array([0, 4, 8]),
        "right_diag": np.array([2, 4, 6]),
    }
    wins_by_position: ClassVar[dict[int, list[str]]] = {
        0: ["top_row", "left_diag", "left_col"],
        1: ["mid_row", "mid_col"],
        2: ["bot_row", "right_diag", "right_col"],
        3: ["top_row", "mid_col"],
        4: ["mid_row", "mid_col", "left_diag", "right_diag"],
        5: ["bot_row", "mid_col"],
        6: ["top_row", "right_diag", "right_col"],
        7: ["mid_row", "right_col"],
        8: ["bot_row", "left_diag", "left_col"],
    }
    player_marks: ClassVar[dict[int, str]] = {0: "X", 1: "O"}
    players: dict[int, TicTacToePlayer] = None
    save_game: dict = None
    num_to_win: ClassVar[int] = 3

    @property
    def current_player(self) -> TicTacToePlayer:
        return self.players[self.current_player_num]

    def model_post_init(self, __context: Any) -> None:
        if self.players is None:
            self.players = {
                player_num: TicTacToePlayer(
                    player_number=player_num, mark=self.player_marks[player_num]
                )
                for player_num in range(self.player_count)
            }
        if self.save_game is None:
            self.save_game = self.model_dump()

    def save_game_state(self) -> dict:
        self.save_game = self.model_dump()

    def load_save_game_state(self):
        save_game = self.save_game
        self.__init__(**save_game)
        self.save_game = save_game

    @property
    def board(self):
        """Just draw an ASCII board."""
        board = f"""\n
        {self.positions[0]}|{self.positions[1]}|{self.positions[2]}       
        _____
        {self.positions[3]}|{self.positions[4]}|{self.positions[5]}
        _____
        {self.positions[6]}|{self.positions[7]}|{self.positions[8]}""".replace(
            f"{TicTacToe.empty_space}", " "
        )
        for player_num, player in self.players.items():
            board = board.replace(str(player_num), player.mark)
        return board

    def draw_board(self):
        print(self.board)

    def get_current_player(self) -> int:
        return self.current_player_num

    def get_available_actions(self, special_policy: bool = False) -> list:
        """Gets available moves in a dictionary.
        The bot will only ever need the keys; values should be unknown
        """
        legal_positions = [
            i
            for i, position in enumerate(self.positions)
            if position == TicTacToe.empty_space
        ]

        # print(f"Original legal actions: {legal_actions}")

        if special_policy and sum(self.positions) > -6:
            special_policy_actions = []
            for position, win_condition_names in self.wins_by_position.items():
                if position not in legal_positions:
                    continue
                for name in win_condition_names:
                    condition_state = self.get_condition_state(
                        self.win_conditions[name]
                    )
                    next_player_num = (self.current_player_num + 1) % self.player_count

                    if (
                        TicTacToe.empty_space in condition_state
                        and condition_state.count(self.current_player_num) == 2
                    ) or (
                        TicTacToe.empty_space in condition_state
                        and condition_state.count(next_player_num) == 2
                    ):
                        special_policy_actions += [
                            self.generate_action_from_position(position)
                        ]
                        break

            if len(special_policy_actions) > 0:

                # print(
                #    f"Available win positions for {self.player_marks[current_player]}, Special policy legal actions: {special_policy_actions}"
                # )
                return special_policy_actions

        legal_actions = [self.generate_action_from_position(i) for i in legal_positions]

        return legal_actions

    def update_game_with_action(
        self, action: TicTacToeAction, player: TicTacToePlayer = None
    ):
        """Makes a move on the board and draws it"""

        self.positions[action.position] = self.current_player_num
        # self.game_over = self.check_game_over()

        self.current_player_num = (self.current_player_num + 1) % self.player_count

    def get_condition_state(self, win_condition: list[int]):
        return [self.positions[num] for num in win_condition]

    def is_game_over(self):
        return self.check_game_over()

    def check_game_over(self):
        """Checks for the eight win conditions, and whether there are moves left.

        Returns:
            bool: Over or not
        """
        if sum(self.positions) < -2:
            return False
        for win_condition in self.win_conditions.values():
            condition_state = self.get_condition_state(win_condition)
            prior_player_num = (self.current_player_num + 1) % self.player_count
            if (
                condition_state.count(condition_state[0]) == TicTacToe.num_to_win
                and condition_state[0] == prior_player_num
            ):
                self.current_player.player_score = -1
                self.players[prior_player_num].player_score = 1
                return True
        if all([pos != TicTacToe.empty_space for pos in self.positions]):
            self.players[0].player_score = 0
            self.players[1].player_score = 0
            return True
        return False

    @property
    def scores(self):
        return {
            player_num: player.player_score
            for player_num, player in self.players.items()
        }

    def get_game_scores(self):
        return self.scores

    def play_game(self):
        while not self.is_game_over():
            pos = int(input("Select a move.  "))
            action = self.generate_action_from_position(pos)
            self.update_game_with_action(action, self.current_player_num)
            print(self.board)
        for player_num, player in self.players.items():
            print(f"{player_num}:  {player.player_score}")

        return self.scores

    def generate_action_from_position(self, position: int):
        action = np.zeros(TicTacToeAction.ACTION_SPACE_SIZE, dtype=int)
        action[position] = 1
        return action.view(TicTacToeAction)


if __name__ == "__main__":
    game = TicTacToe(player_count=2)
    game.play_game()
