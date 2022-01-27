
class Player():
    """No functions, just storage.
    """

    def __init__(self, mark):
        self.mark = mark
        self.score = 0


class Game():
    """Basic game of connect four.

    """
    player_count = 2
    rows = 6
    columns = 7
    win_cnt = 4
    win_points = 10

    def __init__(self, player_count=2):
        """player_count is unused but is generally required for other games, so we add it here.

        Args:
            player_count (int): Player count.  Defaults to 2.
        """
        self.players = {0: Player('X'), 1: Player('O')}
        self.grid = [[" " for i in range(self.rows)]
                     for j in range(self.columns)]
        self.game_over = False
        self.current_player = 0
        self.legal_actions = {}
        self._state = ""

    def test_array(self, test):
        """Simple helper function to determine if an array contains
        four x's or o's

        Args:
            test (list): list on the grid
        """
        return(test.count(test[0]) == len(test)) & (test[0] != " ")

    def is_game_over(self):
        """Tests for four types of wins:  row, column, and both diagonals.
        Also tests for a draw.
        Returns:
            bool: Whether the game is over.
        """
        # Row win
        for row in range(self.rows):
            for column in range(self.columns - self.win_cnt+1):
                test = [self.grid[row][column+k] for k in range(self.win_cnt)]
                if self.test_array(test):
                    self.game_over = True
                    self.players[self.current_player].score = self.win_points
                    return True

        # Column win

        for column in range(self.columns):
            for row in range(self.rows - self.win_cnt+1):
                test = [self.grid[row+k][column] for k in range(self.win_cnt)]
                if self.test_array(test):
                    self.game_over = True
                    return True

        # Down/right diagonal
        for row in range(self.rows - self.win_cnt+1):
            for column in range(self.columns - self.win_cnt+1):
                test = [self.grid[row+k][column+k]
                        for k in range(self.win_cnt)]
                if self.test_array(test):
                    self.game_over = True
                    return True

        # up/right diagonal
        for row in range(self.win_cnt - 1, self.rows):
            for column in range(self.columns - self.win_cnt+1):
                test = [self.grid[row-k][column+k]
                        for k in range(self.win_cnt)]
                if self.test_array(test):
                    self.game_over = True
                    return True

        if not self.get_legal_actions()[0]:
            return True

        return False

    def get_legal_actions(self):
        """Checks which of the columns can have a piece added.

        Returns:
            list: dictionary of legal actions
            int:  current player number
        """
        legal_actions = {}
        act_cnt = 0
        for column in range(self.columns):
            if not all([self.grid[row][column] != " " for row in range(self.rows)]):
                legal_actions[act_cnt] = column
                act_cnt += 1

        if not legal_actions:
            self.game_over = True
        self.legal_actions = legal_actions
        return list(legal_actions.keys()), self.current_player

    def update_game(self, action, player_num):
        """Processes selected action

        Args:
            action (int): lookup index for the selected actions.  Ranges 0-6.
        """
        sel_action = self.legal_actions[action]
        for row in range(self.rows):
            if self.grid[self.rows - row - 1][sel_action] == " ":
                self.grid[self.rows -
                          row - 1][sel_action] = self.players[player_num].mark
                break
        self.current_player = (self.current_player + 1) % self.player_count
        self.is_game_over()
        self.save_state()

    def save_state(self):
        """Saves the game state for printing
        """
        self._state = ""
        for row in range(self.rows):
            self._state += "|".join(self.grid[row][column]
                                    for column in range(self.columns)) + "\n"
            self._state += "_" * (self.columns * 2 - 1) + "\n"

    def game_result(self):
        """Returns the scores

        Returns:
            dict: player number: score
        """
        return {player_num: player.score for player_num, player in self.players.items()}

    def play_game(self):
        self.save_state()
        while not self.is_game_over():
            self.get_legal_actions()
            print(self._state)
            print(self.legal_actions)
            action = int(input("Choose an action"))
            self.update_game(action)


# test = Game(2)

# test.play_game()
