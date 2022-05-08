# %%
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
    win_points = 1

    def __init__(self, player_count=2):
        """player_count is unused but is generally required for other games, so we add it here.

        Args:
            player_count (int): Play0er count.  Defaults to 2.
        """
        self.players = {0: Player('0'), 1: Player('1')}
        self.grid = [[" " for column in range(self.columns)]
                     for row in range(self.rows)]
        self.game_over = False
        self.current_player = 0
        self.legal_actions = {}
        self._state = ""
        self.name = "Connect_Four"
        self.pieces_placed = 0
        self.allowed_columns = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6}

    def test_array(self, test_arr):
        """Simple helper function to determine if an array contains
        four x's or o's

        Args:
            test (list): list on the grid
        """
        return(test_arr.count(test_arr[0]) == len(test_arr)) & (test_arr[0] != " ")

    def is_game_over(self):
        return self.game_over

    def check_game_over(self, latest_piece):
        """Tests for four types of wins:  row, column, and both diagonals.
        Also tests for a draw.
        Returns:
            bool: Whether the game is over.
        """
        win_dict = {'00row': [[0, 0], [0, 1], [0, 2], [0, 3]],
                    '01row': [[0, 1], [0, 2], [0, 3], [0, 4]],
                    '02row': [[0, 2], [0, 3], [0, 4], [0, 5]],
                    '03row': [[0, 3], [0, 4], [0, 5], [0, 6]],
                    '10row': [[1, 0], [1, 1], [1, 2], [1, 3]],
                    '11row': [[1, 1], [1, 2], [1, 3], [1, 4]],
                    '12row': [[1, 2], [1, 3], [1, 4], [1, 5]],
                    '13row': [[1, 3], [1, 4], [1, 5], [1, 6]],
                    '20row': [[2, 0], [2, 1], [2, 2], [2, 3]],
                    '21row': [[2, 1], [2, 2], [2, 3], [2, 4]],
                    '22row': [[2, 2], [2, 3], [2, 4], [2, 5]],
                    '23row': [[2, 3], [2, 4], [2, 5], [2, 6]],
                    '30row': [[3, 0], [3, 1], [3, 2], [3, 3]],
                    '31row': [[3, 1], [3, 2], [3, 3], [3, 4]],
                    '32row': [[3, 2], [3, 3], [3, 4], [3, 5]],
                    '33row': [[3, 3], [3, 4], [3, 5], [3, 6]],
                    '40row': [[4, 0], [4, 1], [4, 2], [4, 3]],
                    '41row': [[4, 1], [4, 2], [4, 3], [4, 4]],
                    '42row': [[4, 2], [4, 3], [4, 4], [4, 5]],
                    '43row': [[4, 3], [4, 4], [4, 5], [4, 6]],
                    '50row': [[5, 0], [5, 1], [5, 2], [5, 3]],
                    '51row': [[5, 1], [5, 2], [5, 3], [5, 4]],
                    '52row': [[5, 2], [5, 3], [5, 4], [5, 5]],
                    '53row': [[5, 3], [5, 4], [5, 5], [5, 6]],
                    '00col': [[0, 0], [1, 0], [2, 0], [3, 0]],
                    '10col': [[1, 0], [2, 0], [3, 0], [4, 0]],
                    '20col': [[2, 0], [3, 0], [4, 0], [5, 0]],
                    '01col': [[0, 1], [1, 1], [2, 1], [3, 1]],
                    '11col': [[1, 1], [2, 1], [3, 1], [4, 1]],
                    '21col': [[2, 1], [3, 1], [4, 1], [5, 1]],
                    '02col': [[0, 2], [1, 2], [2, 2], [3, 2]],
                    '12col': [[1, 2], [2, 2], [3, 2], [4, 2]],
                    '22col': [[2, 2], [3, 2], [4, 2], [5, 2]],
                    '03col': [[0, 3], [1, 3], [2, 3], [3, 3]],
                    '13col': [[1, 3], [2, 3], [3, 3], [4, 3]],
                    '23col': [[2, 3], [3, 3], [4, 3], [5, 3]],
                    '04col': [[0, 4], [1, 4], [2, 4], [3, 4]],
                    '14col': [[1, 4], [2, 4], [3, 4], [4, 4]],
                    '24col': [[2, 4], [3, 4], [4, 4], [5, 4]],
                    '05col': [[0, 5], [1, 5], [2, 5], [3, 5]],
                    '15col': [[1, 5], [2, 5], [3, 5], [4, 5]],
                    '25col': [[2, 5], [3, 5], [4, 5], [5, 5]],
                    '06col': [[0, 6], [1, 6], [2, 6], [3, 6]],
                    '16col': [[1, 6], [2, 6], [3, 6], [4, 6]],
                    '26col': [[2, 6], [3, 6], [4, 6], [5, 6]],
                    '00diag': [[0, 0], [1, 1], [2, 2], [3, 3]],
                    '10diag': [[1, 0], [2, 1], [3, 2], [4, 3]],
                    '20diag': [[2, 0], [3, 1], [4, 2], [5, 3]],
                    '30diag': [[3, 0], [2, 1], [1, 2], [0, 3]],
                    '40diag': [[4, 0], [3, 1], [2, 2], [1, 3]],
                    '50diag': [[5, 0], [4, 1], [3, 2], [2, 3]],
                    '01diag': [[0, 1], [1, 2], [2, 3], [3, 4]],
                    '11diag': [[1, 1], [2, 2], [3, 3], [4, 4]],
                    '21diag': [[2, 1], [3, 2], [4, 3], [5, 4]],
                    '31diag': [[3, 1], [2, 2], [1, 3], [0, 4]],
                    '41diag': [[4, 1], [3, 2], [2, 3], [1, 4]],
                    '51diag': [[5, 1], [4, 2], [3, 3], [2, 4]],
                    '02diag': [[0, 2], [1, 3], [2, 4], [3, 5]],
                    '12diag': [[1, 2], [2, 3], [3, 4], [4, 5]],
                    '22diag': [[2, 2], [3, 3], [4, 4], [5, 5]],
                    '32diag': [[3, 2], [2, 3], [1, 4], [0, 5]],
                    '42diag': [[4, 2], [3, 3], [2, 4], [1, 5]],
                    '52diag': [[5, 2], [4, 3], [3, 4], [2, 5]],
                    '03diag': [[0, 3], [1, 4], [2, 5], [3, 6]],
                    '13diag': [[1, 3], [2, 4], [3, 5], [4, 6]],
                    '23diag': [[2, 3], [3, 4], [4, 5], [5, 6]],
                    '33diag': [[3, 3], [2, 4], [1, 5], [0, 6]],
                    '43diag': [[4, 3], [3, 4], [2, 5], [1, 6]],
                    '53diag ': [[5, 3], [4, 4], [3, 5], [2, 6]], }

        arr_dict = {'00': ['00row', '00col', '00diag'],
                    '01': ['00row', '01row', '01col', '01diag'],
                    '02': ['00row', '01row', '02row', '02col', '02diag'],
                    '03': ['00row', '01row', '02row', '03row', '03col', '30diag', '30diag'],
                    '04': ['01row', '02row', '03row', '04col', '31diag'],
                    '05': ['02row', '03row', '05col', '32diag'],
                    '06': ['03row', '06col', '33diag'],
                    '10': ['10row', '00col', '10col', '10diag'],
                    '11': ['10row', '11row', '01col', '11col', '00diag', '11diag'],
                    '12': ['10row', '11row', '12row', '02col', '12col', '30diag', '30diag', '12diag'],
                    '13': ['10row', '11row', '12row', '13row', '03col', '13col', '13col', '31diag', '02diag', '13diag'],
                    '14': ['11row', '12row', '13row', '04col', '14col', '41diag', '41diag', '03diag'],
                    '15': ['12row', '13row', '05col', '15col', '42diag', '33diag'],
                    '16': ['13row', '06col', '16col', '43diag'],
                    '20': ['20row', '00col', '10col', '20col', '20diag'],
                    '21': ['20row', '21row', '01col', '11col', '21col', '10diag', '10diag', '21diag'],
                    '22': ['20row', '21row', '22row', '02col', '12col', '22col', '22col', '40diag', '11diag', '31diag', '22diag'],
                    '23': ['20row', '21row', '22row', '23row', '03col', '13col', '13col', '50diag', '01diag', '41diag', '12diag', '32diag', '23diag'],
                    '24': ['21row', '22row', '23row', '04col', '14col', '24col', '24col', '02diag', '42diag', '13diag', '33diag'],
                    '25': ['22row', '23row', '05col', '15col', '25col', '52diag', '52diag', '43diag'],
                    '26': ['23row', '06col', '16col', '26col', '53diag'],
                    '30': ['30row', '00col', '10col', '20col', '30diag'],
                    '31': ['30row', '31row', '01col', '11col', '21col', '20diag', '20diag', '31diag'],
                    '32': ['30row', '31row', '32row', '02col', '12col', '22col', '22col', '50diag', '21diag', '41diag', '32diag'],
                    '33': ['30row', '31row', '32row', '33row', '03col', '13col', '13col', '00diag', '11diag', '51diag', '22diag', '42diag', '33diag'],
                    '34': ['31row', '32row', '33row', '04col', '14col', '24col', '24col', '12diag', '52diag', '23diag', '43diag'],
                    '35': ['32row', '33row', '05col', '15col', '25col', '02diag', '02diag', '53diag'],
                    '36': ['33row', '06col', '16col', '26col', '03diag'],
                    '40': ['40row', '10col', '20col', '40diag'],
                    '41': ['40row', '41row', '11col', '21col', '50diag', '41diag'],
                    '42': ['40row', '41row', '42row', '12col', '22col', '20diag', '20diag', '42diag'],
                    '43': ['40row', '41row', '42row', '43row', '13col', '23col', '23col', '21diag', '52diag', '43diag'],
                    '44': ['41row', '42row', '43row', '14col', '24col', '11diag', '11diag', '53diag'],
                    '45': ['42row', '43row', '15col', '25col', '12diag', '23diag'],
                    '46': ['43row', '16col', '26col', '13diag'],
                    '50': ['50row', '20col', '50diag'],
                    '51': ['50row', '51row', '21col', '51diag'],
                    '52': ['50row', '51row', '52row', '22col', '52diag'],
                    '53': ['50row', '51row', '52row', '53row', '23col', '20diag', '20diag'],
                    '54': ['51row', '52row', '53row', '24col', '21diag'],
                    '55': ['52row', '53row', '25col', '22diag'],
                    '56': ['53row', '26col', '23diag'],
                    }

        # Row win

        pot_wins = arr_dict[latest_piece]
        for winkey in pot_wins:
            if winkey in win_dict.keys():
                win_arr = win_dict[winkey]
                test_arr = [self.grid[item[0]][item[1]] for item in win_arr]
                if all([item != " " for item in test_arr]):
                    if self.test_array(test_arr):
                        self.game_over = True
                        self.players[self.current_player].score = self.win_points
                        return True
                    else:
                        win_dict.pop(winkey)

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
        temp_dict = self.allowed_columns.copy()
        for column in temp_dict.keys():
            if not all([self.grid[i][column] != " " for i in range(self.rows)]):
                legal_actions[act_cnt] = column
                act_cnt += 1
            else:
                self.allowed_columns.pop(column)

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
            latest_row = self.rows - row - 1
            if self.grid[latest_row][sel_action] == " ":
                self.grid[latest_row][sel_action] = self.players[player_num].mark
                break
        self.pieces_placed += 1
        if self.pieces_placed > 2 * (self.win_cnt - 1):
            self.check_game_over(f"{latest_row}{sel_action}")
        self.current_player = (self.current_player + 1) % self.player_count
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
        while not self.game_over:
            self.get_legal_actions()
            print(self._state)
            print(self.legal_actions)
            action = int(input("Choose an action"))
            self.update_game(action, self.current_player)


test = Game(2)

test.play_game()
