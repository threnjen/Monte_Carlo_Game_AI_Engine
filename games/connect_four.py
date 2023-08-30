from games.base_game_object import BaseGameObject


class ConnectFour(BaseGameObject):
    """Basic game of connect four."""

    def __init__(self, player_count: int = 2):
        super().__init__(player_count)
        self.player_marks = {0: "X", 1: "O"}
        self.num_columns = 7
        self.positions = [" "] * 42
        self.win_points = 1
        self.win_conditions = self.set_win_dict()
        self.open_columns = [0, 1, 2, 3, 4, 5, 6]

    def get_available_actions(self, special_policy=False) -> list:
        """Checks which of the columns can have a piece added.

        Returns:
            list: dictionary of legal actions
            int:  current player number
        """

        legal_actions = [
            column
            for column in self.open_columns
            if any(self.positions[i] == " " for i in range(column, 42, self.num_columns))
        ]

        if special_policy:  # CURRENTLY NOT WORKING
            special_policy_actions = []
            current_player = self.get_current_player()
            for win_condition in self.win_conditions.values():
                condition_state = self.get_condition_state(win_condition)

                if " " in condition_state and condition_state.count(self.player_marks[current_player]) == 3:
                    win_condition = [x for x in win_condition if self.positions[x] == " "][0]
                    win_condition = win_condition % 7
                    special_policy_actions.append(win_condition)

                next_player = (self.current_player + 1) % self.player_count
                if " " in condition_state and condition_state.count(self.player_marks[next_player]) == 3:
                    win_condition = [x for x in win_condition if self.positions[x] == " "][0]
                    win_condition = win_condition % 7
                    special_policy_actions.append(win_condition)

            special_policy_actions = list(set(special_policy_actions))
            if len(special_policy_actions) > 0:
                # print(
                #     f"Available win positions for {self.player_marks[current_player]}, Special policy legal actions: {special_policy_actions}"
                # )
                return special_policy_actions
        return legal_actions

    def update_game_with_action(self, action, player):
        """Processes selected action

        Args:
            action (int): lookup index for the selected actions.  Ranges 0-6.
        """
        self.make_move(action, player)

    def is_game_over(self):
        """Tests for four types of wins:  row, column, and both diagonals.
        Also tests for a draw.
        Returns:
            bool: Whether the game is over.
        """

        # Row win

        for win_condition in self.win_conditions.values():
            condition_state = self.get_condition_state(win_condition)

            if all(item == self.player_marks[0] for item in condition_state):
                self.scores[0] = 1
                self.scores[1] = -1
                return True
            if all(item == self.player_marks[1] for item in condition_state):
                self.scores[1] = 1
                self.scores[0] = -1
                return True

        avail_actions = self.get_available_actions()

        if len(avail_actions) == 0:
            self.scores[1] = 0
            self.scores[0] = 0

            return True
        else:
            return False

    def draw_board(self):
        board_rows = [
            f"{self.positions[i]}|{self.positions[i+1]}|{self.positions[i+2]}|{self.positions[i+3]}|{self.positions[i+4]}|{self.positions[i+5]}|{self.positions[i+6]}"
            for i in range(0, 42, self.num_columns)
        ]
        board = "\n_____________\n".join(board_rows)
        print(board)

    def play_game(self):
        while not self.is_game_over():
            pos = int(input("Select a move.  "))
            self.make_move(pos, self.current_player)

        for player_num in self.scores.keys():
            print(f"{self.player_count[player_num]}:  {self.scores[player_num]}")

        return self.scores

    def save_game_state(self):
        # self.save_game["positions"] = [x for x in self.positions]
        self.save_game["positions"] = []
        self.save_game["positions"].extend(self.positions)
        self.save_game["scores"] = {x: y for x, y in self.scores.items()}
        self.save_game["current_player"] = self.current_player

    def load_save_game_state(self):
        # self.positions = [x for x in self.save_game["positions"]]
        self.positions = []
        self.positions.extend(self.save_game["positions"])
        self.scores = {x: y for x, y in self.save_game["scores"].items()}
        self.current_player = self.save_game["current_player"]

    def get_condition_state(self, win_condition):
        return [self.positions[num] for num in win_condition]

    def make_move(self, pos: int, current_player: int):
        """Makes a move on the board and draws it"""
        max_position = 42 - (self.num_columns - pos)

        while self.positions[max_position] != " ":
            max_position -= self.num_columns

        self.positions[max_position] = self.player_marks[current_player]

        self.current_player = (self.current_player + 1) % self.player_count

    def set_win_dict(self):
        return {
            "00row": [0, 1, 2, 3],
            "01row": [1, 2, 3, 4],
            "02row": [2, 3, 4, 5],
            "03row": [3, 4, 5, 6],
            "10row": [7, 8, 9, 10],
            "11row": [8, 9, 10, 11],
            "12row": [9, 10, 11, 12],
            "13row": [10, 11, 12, 13],
            "20row": [14, 15, 16, 17],
            "21row": [15, 16, 17, 18],
            "22row": [16, 17, 18, 19],
            "23row": [17, 18, 19, 20],
            "30row": [21, 22, 23, 24],
            "31row": [22, 23, 24, 25],
            "32row": [23, 24, 25, 26],
            "33row": [24, 25, 26, 27],
            "40row": [28, 29, 30, 31],
            "41row": [29, 30, 31, 32],
            "42row": [30, 31, 32, 33],
            "43row": [31, 32, 33, 34],
            "50row": [35, 36, 37, 38],
            "51row": [36, 37, 38, 39],
            "52row": [37, 38, 39, 40],
            "53row": [38, 39, 40, 41],
            "00col": [0, 7, 14, 21],
            "10col": [7, 14, 21, 28],
            "20col": [14, 21, 28, 35],
            "01col": [1, 8, 15, 22],
            "11col": [8, 15, 22, 29],
            "21col": [15, 22, 29, 36],
            "02col": [2, 9, 16, 23],
            "12col": [9, 16, 23, 30],
            "22col": [16, 23, 30, 37],
            "03col": [3, 10, 17, 24],
            "13col": [10, 17, 24, 31],
            "23col": [17, 24, 31, 38],
            "04col": [4, 11, 18, 25],
            "14col": [11, 18, 25, 32],
            "24col": [18, 25, 32, 39],
            "05col": [5, 12, 19, 26],
            "15col": [12, 19, 26, 33],
            "25col": [19, 26, 33, 40],
            "06col": [6, 13, 20, 27],
            "16col": [13, 20, 27, 34],
            "26col": [20, 27, 34, 41],
            "00diag": [0, 8, 16, 24],
            "10diag": [7, 15, 23, 31],
            "20diag": [14, 22, 30, 38],
            "30diag": [21, 15, 9, 3],
            "40diag": [28, 22, 16, 10],
            "50diag": [35, 29, 23, 17],
            "01diag": [1, 9, 17, 25],
            "11diag": [8, 16, 24, 32],
            "21diag": [15, 23, 31, 39],
            "31diag": [22, 16, 10, 4],
            "41diag": [29, 23, 17, 11],
            "51diag": [36, 30, 24, 18],
            "02diag": [2, 10, 18, 26],
            "12diag": [9, 17, 25, 33],
            "22diag": [16, 24, 32, 40],
            "32diag": [23, 17, 11, 5],
            "42diag": [30, 24, 18, 12],
            "52diag": [37, 31, 25, 19],
            "03diag": [3, 11, 19, 27],
            "13diag": [10, 18, 26, 34],
            "23diag": [17, 25, 33, 41],
            "33diag": [24, 18, 12, 6],
            "43diag": [31, 25, 19, 13],
            "53diag ": [38, 32, 26, 20],
        }
