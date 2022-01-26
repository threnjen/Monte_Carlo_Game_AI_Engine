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
        #self.legal_actions = {}
        self.players = {0: Player("0"), 1: Player("1")}
        self.scores = {0: 0, 1: 0}
        self.game_over = False
        self.current_player_num = 0
        self._state = ""
        self.draw_board()

        self.win_conditions = {"top_row": [0, 1, 2],
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

        for win_condition in self.win_conditions.values():

            condition_state = [self.positions[num] for num in win_condition]           
            #empty = len([i for i in condition_state if i ==' '])
            #for player in self.players:
                #print(len([i for i in condition_state if i==self.players[player].mark])==2)

            #print("Win condition being checked: "+str(win_condition))
            #print("Win condition current state: "+str(condition_state))
            #print("Win condition slots like first slot: "+str(condition_state.count(condition_state[0])))
            #print("Win condition slots like second slot: "+str(condition_state.count(condition_state[1])))
            #print("Win condition slots like second slot: "+str(condition_state.count(condition_state[2])))
            #print("Win condition slot[0]: "+str(condition_state[0]))
            #print("Win condition slot[1]: "+str(condition_state[1]))
            #print("Win condition slot[2]: "+str(condition_state[2]))
            #print("Slots that are empty: "+str(empty))
            #print('\n')

            # this counts if all of the slots are the same as the first slot of the condition state, and that the slot is not empty
            if condition_state.count(condition_state[0]) == len(condition_state) and condition_state[0] != " ":
                open_positions = sum(x == ' ' for x in self.positions)
                if self.players[0].mark == condition_state[0]:
                    self.scores[0] = 10   
                    self.scores[1] = -10# - 10*open_positions
                elif self.players[1].mark == condition_state[0]:
                    self.scores[1] = 10
                    self.scores[0] = -10# - 10*open_positions
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
            #print(self._state)

        for player_num in self.scores.keys():
            print(
                f"{self.players[player_num].mark}:  {self.scores[player_num]}")

        return self.scores

#test = Game()

#test.play_game()
