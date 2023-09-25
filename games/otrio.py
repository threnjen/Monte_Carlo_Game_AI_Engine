from cgi import test
import numpy as np

from games.base_game_object import GameEnvironment


class Player:
    def __init__(self, mark, id):

        self.mark = mark
        self.id = id

        self.pieces = {}
        self.pieces[0] = [mark, mark, mark]
        self.pieces[1] = [mark, mark, mark]
        self.pieces[2] = [mark, mark, mark]


class Otrio(GameEnvironment):
    def __init__(self, player_count):

        self.board = np.zeros((3, 3, 3)).astype("int")
        self.game_over = False
        self.state = ""
        self.scores = {n + 1: 0 for n in range(player_count)}
        self.current_player_num = 1
        self.turn = 0
        self.player_count = self._set_player_count(player_count)
        self._create_win_position_ref()  # Build game board win matrix

    def _set_player_count(self, player_count):
        if player_count >= 2:
            player_count_dict = {1: Player(1, 1), 2: Player(2, 2)}
        if player_count >= 3:
            player_count_dict[3] = Player(3, 3)
        if player_count == 4:
            player_count_dict[4] = Player(4, 4)
        if player_count < 2 or player_count > 4:
            print("Invalid player number selection. Must enter player_count from 2-4")
        return player_count_dict

    def _make_move(self, action, current_player_num):

        self.turn += 1
        position = tuple(action)
        self.board[position] = (
            self.player_count[current_player_num].pieces[action[0]].pop()
        )

        remove_conditions = []
        lookup_index = str(action)
        # print(f"Chosen action being checked: {lookup_index}")

        for current_win_condition in self.win_conditions[lookup_index]:
            # print(f"Win condition being checked: {current_win_condition}")

            test_indices = [tuple(x) for x in current_win_condition]
            check_current_marks = [self.board[i] for i in test_indices]
            # print(f"Player pieces in this condition: {check_current_marks}")

            if 0 not in check_current_marks and not all(
                element == check_current_marks[0] for element in check_current_marks
            ):
                # print(
                #    f"win condition is now blocked, appending to remove {current_win_condition}"
                # )
                remove_conditions.append(current_win_condition)
            elif 0 not in check_current_marks and all(
                element == check_current_marks[0] for element in check_current_marks
            ):
                # print("win condition achieved, updated self.game_over = True")
                player_winner = check_current_marks[0]
                self.scores[player_winner] = 1
                for k in self.scores.keys():
                    if k != player_winner:
                        self.scores[k] = -1
                self.game_over = True
            else:
                continue

        if remove_conditions:
            # print(f"Remove these conditions: {lookup_index}: {remove_conditions}")
            for item in remove_conditions:
                self.win_conditions[lookup_index].remove(item)

        self.current_player_num = (
            1
            if self.current_player_num == max(self.scores.keys())
            else self.current_player_num + 1
        )

    def get_current_player(self):
        return self.current_player_num

    def get_available_actions(self, special_policy=False):

        current_player = self.current_player_num
        invalid_player_levels = [
            k
            for k, v in self.player_count[current_player].pieces.items()
            if len(v) == 0
        ]

        legal_actions = np.argwhere(self.board == 0).tolist()
        legal_actions = [x for x in legal_actions if x[0] not in invalid_player_levels]

        if special_policy:

            for potential_win_current_player in legal_actions:

                potential_win_current_action = self.check_player_kill_moves(
                    potential_win_current_player, current_player
                )
                if potential_win_current_action:
                    return potential_win_current_action

            for potential_win_next_player in legal_actions:
                next_player = (
                    1
                    if current_player == max(self.scores.keys())
                    else current_player + 1
                )

                potential_win_next_action = self.check_player_kill_moves(
                    potential_win_next_player, next_player
                )
                if potential_win_next_action:
                    return potential_win_next_action

        return legal_actions

    def check_player_kill_moves(self, move, player):
        for current_win_condition in self.win_conditions[str(move)]:

            test_indices = [tuple(x) for x in current_win_condition]
            check_current_marks = [self.board[i] for i in test_indices]

            if check_current_marks.count(0) == 1 and len(set(check_current_marks)) == 2:
                if player in check_current_marks:
                    # print(f"Player {player} kill move found: {move}")
                    return [move]

            return []

    def update_game_with_action(self, action, player):

        self._make_move(action, player)

    def is_game_over(self):
        # print(f"Game over? {self.game_over}")

        avail_actions = self.get_available_actions()
        if len(avail_actions) == 0:
            self.game_over = True
            return self.game_over
        else:
            return self.game_over

    def get_game_scores(self):

        return self.scores

    def draw_board(self):

        self.board_draw = f"""
        Level 1\t\t\tLevel 2\t\t\tLevel 3\n
        {self.board[0,0,0]}|{self.board[0,0,1]}|{self.board[0,0,2]}\t\t\t{self.board[1,0,0]}|{self.board[1,0,1]}|{self.board[1,0,2]}\t\t\t{self.board[2,0,0]}|{self.board[2,0,1]}|{self.board[2,0,2]}       
        _____\t\t\t_____\t\t\t_____
        {self.board[0,1,0]}|{self.board[0,1,1]}|{self.board[0,1,2]}\t\t\t{self.board[1,1,0]}|{self.board[1,1,1]}|{self.board[1,1,2]}\t\t\t{self.board[2,1,0]}|{self.board[2,1,1]}|{self.board[2,1,2]}
        _____\t\t\t_____\t\t\t_____
        {self.board[0,2,0]}|{self.board[0,2,1]}|{self.board[0,2,2]}\t\t\t{self.board[1,2,0]}|{self.board[1,2,1]}|{self.board[1,2,2]}\t\t\t{self.board[2,2,0]}|{self.board[2,2,1]}|{self.board[2,2,2]}
        """

        print(self.board_draw)

    def play_game(self):

        while not self.is_game_over():

            pos = int(input("Select a move.  "))
            self._make_move(pos, self.current_player_num)

        for player_num in self.scores.keys():
            print(f"{self.player_count[player_num].mark}:  {self.scores[player_num]}")

        return self.scores

    def _create_win_position_ref(self):
        self.win_conditions = {
            "[0, 0, 0]": [
                [[0, 0, 0], [0, 0, 1], [0, 0, 2]],
                [[0, 0, 0], [0, 1, 0], [0, 2, 0]],
                [[0, 0, 0], [0, 1, 1], [0, 2, 2]],
                [[0, 0, 0], [1, 0, 0], [2, 0, 0]],
                [[0, 0, 0], [1, 0, 1], [2, 0, 2]],
                [[0, 0, 0], [1, 1, 0], [2, 2, 0]],
                [[0, 0, 0], [1, 1, 1], [2, 2, 2]],
            ],
            "[0, 1, 0]": [
                [[0, 1, 0], [0, 1, 1], [0, 1, 2]],
                [[0, 0, 0], [0, 1, 0], [0, 2, 0]],
                [[0, 1, 0], [1, 1, 0], [2, 1, 0]],
                [[0, 1, 0], [1, 1, 1], [2, 1, 2]],
            ],
            "[0, 2, 0]": [
                [[0, 2, 0], [0, 2, 1], [0, 2, 2]],
                [[0, 0, 0], [0, 1, 0], [0, 2, 0]],
                [[0, 0, 2], [0, 1, 1], [0, 2, 0]],
                [[0, 2, 0], [1, 2, 0], [2, 2, 0]],
                [[0, 2, 0], [1, 2, 1], [2, 2, 2]],
                [[0, 2, 0], [1, 1, 0], [2, 0, 0]],
                [[0, 2, 0], [1, 1, 1], [2, 0, 2]],
            ],
            "[0, 0, 1]": [
                [[0, 0, 0], [0, 0, 1], [0, 0, 2]],
                [[0, 0, 1], [1, 0, 1], [2, 0, 1]],
                [[0, 0, 1], [1, 1, 1], [2, 2, 1]],
                [[0, 0, 1], [0, 1, 1], [0, 2, 1]],
            ],
            "[0, 0, 2]": [
                [[0, 0, 0], [0, 0, 1], [0, 0, 2]],
                [[0, 0, 2], [0, 1, 1], [0, 2, 0]],
                [[0, 0, 2], [1, 0, 2], [2, 0, 2]],
                [[2, 0, 0], [1, 0, 1], [0, 0, 2]],
                [[0, 0, 2], [1, 1, 2], [2, 2, 2]],
                [[2, 2, 0], [1, 1, 1], [0, 0, 2]],
                [[0, 1, 2], [0, 2, 2], [0, 0, 2]],
            ],
            "[0, 1, 1]": [
                [[0, 1, 0], [0, 1, 1], [0, 1, 2]],
                [[0, 0, 0], [0, 1, 1], [0, 2, 2]],
                [[0, 0, 2], [0, 1, 1], [0, 2, 0]],
                [[0, 1, 1], [1, 1, 1], [2, 1, 1]],
                [[0, 0, 1], [0, 1, 1], [0, 2, 1]],
            ],
            "[0, 1, 2]": [
                [[0, 1, 0], [0, 1, 1], [0, 1, 2]],
                [[0, 1, 2], [1, 1, 2], [2, 1, 2]],
                [[2, 1, 0], [1, 1, 1], [0, 1, 2]],
                [[0, 1, 2], [0, 2, 2], [0, 0, 2]],
            ],
            "[0, 2, 1]": [
                [[0, 2, 0], [0, 2, 1], [0, 2, 2]],
                [[0, 2, 1], [1, 2, 1], [2, 2, 1]],
                [[0, 2, 1], [1, 1, 1], [2, 0, 1]],
                [[0, 0, 1], [0, 1, 1], [0, 2, 1]],
            ],
            "[0, 2, 2]": [
                [[0, 2, 0], [0, 2, 1], [0, 2, 2]],
                [[0, 0, 0], [0, 1, 1], [0, 2, 2]],
                [[0, 2, 2], [1, 2, 2], [2, 2, 2]],
                [[2, 2, 0], [1, 2, 1], [0, 2, 2]],
                [[2, 0, 0], [1, 1, 1], [0, 2, 2]],
                [[0, 1, 2], [0, 2, 2], [0, 0, 2]],
                [[0, 2, 2], [1, 1, 2], [2, 0, 2]],
            ],
            "[1, 0, 0]": [
                [[1, 0, 0], [1, 0, 1], [1, 0, 2]],
                [[1, 0, 0], [1, 1, 0], [1, 2, 0]],
                [[1, 0, 0], [1, 1, 1], [1, 2, 2]],
                [[0, 0, 0], [1, 0, 0], [2, 0, 0]],
            ],
            "[1, 1, 0]": [
                [[1, 1, 0], [1, 1, 1], [1, 1, 2]],
                [[1, 0, 0], [1, 1, 0], [1, 2, 0]],
                [[0, 1, 0], [1, 1, 0], [2, 1, 0]],
                [[0, 0, 0], [1, 1, 0], [2, 2, 0]],
                [[0, 2, 0], [1, 1, 0], [2, 0, 0]],
            ],
            "[1, 2, 0]": [
                [[1, 2, 0], [1, 2, 1], [1, 2, 2]],
                [[1, 0, 0], [1, 1, 0], [1, 2, 0]],
                [[1, 0, 2], [1, 1, 1], [1, 2, 0]],
                [[0, 2, 0], [1, 2, 0], [2, 2, 0]],
            ],
            "[1, 0, 1]": [
                [[1, 0, 0], [1, 0, 1], [1, 0, 2]],
                [[1, 0, 1], [1, 1, 1], [1, 2, 1]],
                [[0, 0, 1], [1, 0, 1], [2, 0, 1]],
                [[0, 0, 0], [1, 0, 1], [2, 0, 2]],
                [[2, 0, 0], [1, 0, 1], [0, 0, 2]],
            ],
            "[1, 0, 2]": [
                [[1, 0, 0], [1, 0, 1], [1, 0, 2]],
                [[1, 0, 2], [1, 1, 2], [1, 2, 2]],
                [[1, 0, 2], [1, 1, 1], [1, 2, 0]],
                [[0, 0, 2], [1, 0, 2], [2, 0, 2]],
            ],
            "[1, 1, 1]": [
                [[1, 1, 0], [1, 1, 1], [1, 1, 2]],
                [[1, 0, 1], [1, 1, 1], [1, 2, 1]],
                [[1, 0, 0], [1, 1, 1], [1, 2, 2]],
                [[1, 0, 2], [1, 1, 1], [1, 2, 0]],
                [[0, 1, 1], [1, 1, 1], [2, 1, 1]],
                [[0, 1, 0], [1, 1, 1], [2, 1, 2]],
                [[0, 0, 1], [1, 1, 1], [2, 2, 1]],
                [[0, 2, 1], [1, 1, 1], [2, 0, 1]],
                [[2, 1, 0], [1, 1, 1], [0, 1, 2]],
                [[2, 0, 0], [1, 1, 1], [0, 2, 2]],
                [[0, 2, 0], [1, 1, 1], [2, 0, 2]],
                [[2, 2, 0], [1, 1, 1], [0, 0, 2]],
                [[0, 0, 0], [1, 1, 1], [2, 2, 2]],
            ],
            "[1, 1, 2]": [
                [[1, 1, 0], [1, 1, 1], [1, 1, 2]],
                [[1, 0, 2], [1, 1, 2], [1, 2, 2]],
                [[0, 1, 2], [1, 1, 2], [2, 1, 2]],
                [[0, 0, 2], [1, 1, 2], [2, 2, 2]],
                [[0, 2, 2], [1, 1, 2], [2, 0, 2]],
            ],
            "[1, 2, 1]": [
                [[1, 2, 0], [1, 2, 1], [1, 2, 2]],
                [[1, 0, 1], [1, 1, 1], [1, 2, 1]],
                [[0, 2, 1], [1, 2, 1], [2, 2, 1]],
                [[0, 2, 0], [1, 2, 1], [2, 2, 2]],
                [[2, 2, 0], [1, 2, 1], [0, 2, 2]],
            ],
            "[1, 2, 2]": [
                [[1, 2, 0], [1, 2, 1], [1, 2, 2]],
                [[1, 0, 2], [1, 1, 2], [1, 2, 2]],
                [[1, 0, 0], [1, 1, 1], [1, 2, 2]],
                [[0, 2, 2], [1, 2, 2], [2, 2, 2]],
            ],
            "[2, 0, 0]": [
                [[2, 0, 0], [2, 0, 1], [2, 0, 2]],
                [[2, 0, 0], [2, 1, 0], [2, 2, 0]],
                [[2, 0, 0], [2, 1, 1], [2, 2, 2]],
                [[0, 0, 0], [1, 0, 0], [2, 0, 0]],
                [[2, 0, 0], [1, 0, 1], [0, 0, 2]],
                [[0, 2, 0], [1, 1, 0], [2, 0, 0]],
                [[2, 0, 0], [1, 1, 1], [0, 2, 2]],
            ],
            "[2, 1, 0]": [
                [[2, 1, 0], [2, 1, 1], [2, 1, 2]],
                [[2, 0, 0], [2, 1, 0], [2, 2, 0]],
                [[0, 1, 0], [1, 1, 0], [2, 1, 0]],
                [[2, 1, 0], [1, 1, 1], [0, 1, 2]],
            ],
            "[2, 2, 0]": [
                [[2, 2, 0], [2, 2, 1], [2, 2, 2]],
                [[2, 0, 0], [2, 1, 0], [2, 2, 0]],
                [[0, 2, 0], [1, 2, 0], [2, 2, 0]],
                [[2, 2, 0], [1, 2, 1], [0, 2, 2]],
                [[0, 0, 0], [1, 1, 0], [2, 2, 0]],
                [[2, 2, 0], [1, 1, 1], [0, 0, 2]],
                [[2, 2, 0], [2, 1, 1], [2, 0, 2]],
            ],
            "[2, 0, 1]": [
                [[2, 0, 0], [2, 0, 1], [2, 0, 2]],
                [[2, 0, 1], [2, 1, 1], [2, 2, 1]],
                [[0, 0, 1], [1, 0, 1], [2, 0, 1]],
                [[0, 2, 1], [1, 1, 1], [2, 0, 1]],
            ],
            "[2, 0, 2]": [
                [[2, 0, 0], [2, 0, 1], [2, 0, 2]],
                [[2, 0, 2], [2, 1, 2], [2, 2, 2]],
                [[0, 0, 2], [1, 0, 2], [2, 0, 2]],
                [[0, 0, 0], [1, 0, 1], [2, 0, 2]],
                [[0, 2, 0], [1, 1, 1], [2, 0, 2]],
                [[0, 2, 2], [1, 1, 2], [2, 0, 2]],
                [[2, 2, 0], [2, 1, 1], [2, 0, 2]],
            ],
            "[2, 1, 1]": [
                [[2, 1, 0], [2, 1, 1], [2, 1, 2]],
                [[2, 0, 1], [2, 1, 1], [2, 2, 1]],
                [[2, 0, 0], [2, 1, 1], [2, 2, 2]],
                [[0, 1, 1], [1, 1, 1], [2, 1, 1]],
                [[2, 2, 0], [2, 1, 1], [2, 0, 2]],
            ],
            "[2, 1, 2]": [
                [[2, 1, 0], [2, 1, 1], [2, 1, 2]],
                [[2, 0, 2], [2, 1, 2], [2, 2, 2]],
                [[0, 1, 2], [1, 1, 2], [2, 1, 2]],
                [[0, 1, 0], [1, 1, 1], [2, 1, 2]],
            ],
            "[2, 2, 1]": [
                [[2, 2, 0], [2, 2, 1], [2, 2, 2]],
                [[2, 0, 1], [2, 1, 1], [2, 2, 1]],
                [[0, 2, 1], [1, 2, 1], [2, 2, 1]],
                [[0, 0, 1], [1, 1, 1], [2, 2, 1]],
            ],
            "[2, 2, 2]": [
                [[2, 2, 0], [2, 2, 1], [2, 2, 2]],
                [[2, 0, 2], [2, 1, 2], [2, 2, 2]],
                [[0, 2, 2], [1, 2, 2], [2, 2, 2]],
                [[0, 2, 0], [1, 2, 1], [2, 2, 2]],
                [[0, 0, 2], [1, 1, 2], [2, 2, 2]],
                [[0, 0, 0], [1, 1, 1], [2, 2, 2]],
                [[2, 0, 0], [2, 1, 1], [2, 2, 2]],
            ],
        }
        self.unique_win_conditions = []

        for group in self.win_conditions.values():
            for win_set in group:
                if win_set not in self.unique_win_conditions:
                    self.unique_win_conditions.append(win_set)


if __name__ == "__main__":
    game = Otrio(4)
    game.play_game()
