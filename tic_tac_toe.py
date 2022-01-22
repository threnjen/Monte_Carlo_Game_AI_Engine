from locale import currency
from random import choice


def call_monte_carlo(arr):
    pass


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
        self.isbot = isbot


class Game():
    """Tic tac toe game
    """
    win_arr = {"top_row": [0, 1, 2],
               "left_diag": [0, 4, 8],
               "mid_row": [3, 4, 5],
               "bot_row": [6, 7, 8],
               "right_diag": [6, 4, 2],
               "left_col": [0, 3, 6],
               "mid_col": [1, 4, 7],
               "right_col": [2, 5, 8]}

    player_count = 2

    def __init__(self):
        """Calling the game doesn't create any unique starting conditions,
        since there are always two players.
        """
        self.positions = [" "] * 9
        self.available_moves = {}
        self.players = {0: Player("X"), 1: Player("O")}
        self.scores = {0: 0, 1: 0}
        self.game_over = False
        self.current_player_num = 0

    def draw_board(self):
        """Just draw an ASCII board.
        """
        print(f"{self.positions[0]}|{self.positions[1]}|{self.positions[2]}")
        print("_____")
        print(f"{self.positions[3]}|{self.positions[4]}|{self.positions[5]}")
        print("_____")
        print(f"{self.positions[6]}|{self.positions[7]}|{self.positions[8]}")

    def get_available_moves(self):
        """Gets available moves in a dictionary.
        The bot will only ever need the keys; values should be unknown

        Returns:
            dict: integer/move pairs.
        """
        i = 0
        self.available_moves = {}
        for pos in range(self.positions):
            if self.positions[pos] == " ":
                self.available_moves[i] = pos
        return self.available_moves

    def make_move(self, pos, current_player_num):
        """Makes a move on the board and draws it

        Args:
            pos (int): Position on board
            current_player_num (int): Player number, used to lookup the appropriate mark
        """
        self.positions[pos] = self.players[current_player_num].mark
        self.draw_board()

    def take_turn(self, pos, current_player_num, bot_sim=False):
        """Takes a turn, which is simply a "make move" unless the bot is playing.
        If the bot is playing AND this is a simulation run, it then makes a 
        random move for the next player as well.

        Args:
            pos (int): Position on board
            current_player_num (int): Player number, used to lookup the player mark
            bot_sim (bool, optional): Whether this is a bot simulation (for rolling out the board).
            Note this key can also be used to simulate games with a dummy opponent (I think).
            Defaults to False.
        """
        self.make_move(pos, current_player_num)
        if bot_sim:
            next_player = current_player_num + 1
            while next_player % Game.player_count != current_player_num:
                self.take_random_move(self.players[next_player])
                self.draw_board()
                next_player += 1

    def take_random_move(self, current_player_num):
        """Allows a dummy player to make a mark

        Args:
            current_player_num (int): Player number
        """
        pos = choice(self.get_available_moves.values())
        self.make_move(pos, current_player_num)

    def check_win(self):
        """Checks for the eight win conditions.

        Returns:
            bool: Win or not
        """
        for arr in Game.win_arr.values():
            win_arr = [self.positions[num] for num in arr]
            if win_arr.count(win_arr[0]) == len(win_arr):
                return True

        return False

    def play_game(self, sim_run=False):
        """Plays out the game.  This always starts from the current player.
        I think this can be called by the bot when needed.  If the bot needs to
        simulate more runs, that can be controlled here (though the flag does nothing
        presently).

        Args:
            sim_run (bool, optional): Whether this is a simulation run. Defaults to False.

        Returns:
            scores: player score dictionary
        """
        while self.get_available_moves and not self.game_over:
            if self.players[self.current_player_num].isbot:
                move, bot_sim = call_monte_carlo(
                    self.get_available_moves, self, self.current_player_num)
                self.take_turn(move, self.current_player_num, bot_sim)
            else:
                pos = int(input("Select a move.  "))
                self.take_turn(pos, self.current_player_num)
            if self.check_win() == self.players[self.current_player_num].mark:
                self.scores[self.current_player_num] = 10
                self.scores[self.current_player_num] = -10

                self.game_over = True
                return self.scores
            self.current_player_num = (
                self.current_player_num + 1) % Game.player_count

    def get_player_score(self, player_num):
        """Returns score of a player.  Useful to be called by the bot.

        Args:
            player_num (int): player_number

        Returns:
            int: Player score
        """
        return self.scores[player_num]

    def clone_game(self, game_state, bot_sim=False):
        self = game_state.copy()
        self.play_game(bot_sim)


test = Game()

test.play_game()
