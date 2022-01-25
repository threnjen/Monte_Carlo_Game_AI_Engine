from random import choice

from pandas import array


class Player():
    """Player class.  Not much here
    """

    def __init__(self, mark, isbot=False):
        """Player class

        Args:
            mark (str): X or O
            isbot (bool, optional): Whether this is a bot. Defaults to False.
        """
        self.mark = mark


class Game():
    """Tic tac toe game
    """

    def __init__(self):
        """Calling the game doesn't create any unique starting conditions,
        since there are always two players.
        """
        self.positions = [" "] * 9
        self.legal_actions = {}
        self.players = {0: Player("X"), 1: Player("O")}
        self.scores = {0: 0, 1: 0}
        self.game_over = False
        self.current_player_num = 0
        self._state = ""
        self.draw_board()

        self.win_arr = {"top_row": [0, 1, 2],
               "left_diag": [0, 4, 8],
               "mid_row": [3, 4, 5],
               "bot_row": [6, 7, 8],
               "right_diag": [6, 4, 2],
               "left_col": [0, 3, 6],
               "mid_col": [1, 4, 7],
               "right_col": [2, 5, 8]}

        self.player_count = 2

    def draw_board(self):
        """Just draw an ASCII board.
        """
        self._state = f"""\n
        {self.positions[0]}|{self.positions[1]}|{self.positions[2]}       
        _____
        {self.positions[3]}|{self.positions[4]}|{self.positions[5]}
        _____
        {self.positions[6]}|{self.positions[7]}|{self.positions[8]}"""

        #print(self._state)

    def make_move(self, pos, current_player_num):
        """Makes a move on the board and draws it

        Args:
            pos (int): Position on board
            current_player_num (int): Player number, used to lookup the appropriate mark
        """
        self.positions[pos] = self.players[current_player_num].mark
        self.draw_board()
        self.current_player_num = (
            self.current_player_num + 1) % self.player_count


    def get_legal_actions(self):
        """Gets available moves in a dictionary.
        The bot will only ever need the keys; values should be unknown

        Returns:
            dict: integer/move pairs.
        """
        self.legal_actions = []
        for pos in range(len(self.positions)):
            #print(self.positions)
            if self.positions[pos] == " ":
                self.legal_actions.append(pos)
        return [self.legal_actions, self.current_player_num]        

    def update_game(self, action, player):
        #pos = self.legal_actions[action]
        pos = action
        self.make_move(pos, player)

    def is_game_over(self):
        """Checks for the eight win conditions, and whether there are moves left.

        Returns:
            bool: Over or not
        """
        avail_actions = self.get_legal_actions()[0]

        for arr in self.win_arr.values():
            win_arr = [self.positions[num] for num in arr]
            if win_arr.count(win_arr[0]) == len(win_arr) and win_arr[0] != " ":
                open_positions = sum(x == ' ' for x in self.positions)
                if self.players[0].mark == win_arr[0]:
                    self.scores[0] = 10 + 10*open_positions     
                    self.scores[1] = -10 - 10*open_positions
                elif self.players[1].mark == win_arr[0]:
                    self.scores[1] = 10 + 10*open_positions     
                    self.scores[0] = -10 - 10*open_positions
                return True
        
        if len(avail_actions) == 0:

            return True
        else:
            return False

    def game_result(self):
        return self.scores

    def play_game(self):
        while not self.is_game_over():
            pos = int(input("Select a move.  "))
            self.make_move(pos, self.current_player_num)

        for player_num in self.scores.keys():
            print(
                f"{self.players[player_num].mark}:  {self.scores[player_num]}")

        return self.scores

#test = Game()

#test.play_game()
