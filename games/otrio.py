from cgi import test
import numpy as np

from games.game_class import Game


class Player:
    def __init__(self, mark, id):

        self.mark = mark
        self.id = id

        self.pieces = {}
        self.pieces[0] = [mark, mark, mark]
        self.pieces[1] = [mark, mark, mark]
        self.pieces[2] = [mark, mark, mark]


class Otrio(Game):
    def __init__(self, player_count):

        self.board = np.zeros((3, 3, 3)).astype("int")
        self.game_over = False
        self.state = ""
        self.draw_board()
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
        player_marker = self.player_count[current_player_num].pieces[action[0]].pop()
        self.board[position] = player_marker
        self.draw_board()

        # call game over conditions here

        remove_conditions = []
        lookup_index = str(action)

        for single_win_condition in self.win_position_ref[lookup_index]:

            test_indices = [tuple(x) for x in single_win_condition]
            test_win_contents = [self.board[i] for i in test_indices]

            if 0 not in test_win_contents and not all(
                element == test_win_contents[0] for element in test_win_contents
            ):
                remove_conditions.append(lookup_index)
            elif 0 not in test_win_contents and all(
                element == test_win_contents[0] for element in test_win_contents
            ):
                player_winner = test_win_contents[0]
                self.scores[player_winner] = 1 + len(np.nonzero(self.board))
                for k in self.scores.keys():
                    if k != player_winner:
                        self.scores[k] = -1 - len(np.nonzero(self.board))
                self.game_over = True
                # print(single_win_condition)
            else:
                continue

        remove_conditions = list(set(remove_conditions))
        for item in remove_conditions:
            del self.win_position_ref[item]

        if self.current_player_num == max(self.scores.keys()):
            self.current_player_num = 1
        else:
            self.current_player_num += 1

    def get_legal_actions(self, policy=False):

        current_player = self.current_player_num
        # print("Current player: "+str(current_player))
        invalid_player_levels = [
            k for k, v in self.player_count[current_player].pieces.items() if len(v) == 0
        ]

        legal_actions = np.argwhere(self.board == 0).tolist()
        legal_actions = [x for x in legal_actions if x[0] not in invalid_player_levels]

        if policy == True:
            for potential_kill_move in legal_actions:

                for single_win_condition in self.win_position_ref[
                    str(potential_kill_move)
                ]:

                    test_indices = [tuple(x) for x in single_win_condition]
                    test_win_contents = [self.board[i] for i in test_indices]

                    if test_win_contents.count(current_player) == 2:
                        # print("killing move for this player "+str(current_player))
                        # print(test_win_contents, potential_kill_move)
                        legal_actions = [potential_kill_move]
                        return [legal_actions, self.current_player_num]
                    else:
                        pass

            for potential_kill_move in legal_actions:

                for single_win_condition in self.win_position_ref[
                    str(potential_kill_move)
                ]:

                    test_indices = [tuple(x) for x in single_win_condition]
                    test_win_contents = [self.board[i] for i in test_indices]

                    if test_win_contents.count(0) == 1:
                        if len(set(test_win_contents)) == 2:
                            legal_actions = [potential_kill_move]
                            if current_player == max(self.scores.keys()):
                                next_player = 1
                            else:
                                next_player = current_player + 1
                            if test_win_contents.count(next_player) == 2:
                                # print("killing move for next player after "+str(current_player))
                                # print(test_win_contents, potential_kill_move)
                                legal_actions = [potential_kill_move]
                                return [legal_actions, self.current_player_num]
                            else:
                                # print("killing move for other player besides "+str(current_player))
                                # print(test_win_contents, potential_kill_move)
                                return [legal_actions, self.current_player_num]

                    else:
                        pass

        return [legal_actions, self.current_player_num]

    def update_game(self, action, player):

        self._make_move(action, player)

    def is_game_over(self):

        avail_actions = self.get_legal_actions()[0]
        if len(avail_actions) == 0:
            self.game_over = True
            return self.game_over
        else:
            return self.game_over

    def game_result(self):

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
        self.win_position_ref = {
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


if __name__ == "__main__":
    game = Otrio(4)
    game.play_game()
