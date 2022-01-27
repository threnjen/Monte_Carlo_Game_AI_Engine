
class Player():

    def __init__(self, mark):
        self.mark = mark
        self.score = 0


class Game():
    player_count = 2
    rows = 7
    columns = 7
    win_cnt = 4
    win_points = 10

    def __init__(self, player_count):
        self.players = {0: Player('X'), 1: Player('O')}
        self.grid = [[" " for i in range(self.rows)]
                     for j in range(self.columns)]
        self.game_over = False
        self.current_player = 0
        self.legal_actions = {}
        self.state = ""

    # def get_legal_actions(self):
    #     legal_moves = {}
    #     for j in range(self.columns):
    #         legal_moves[j] = not all(
    #             [self.grid[i][j] != " " for i in range(self.rows())])
    #     return {key: value for key, value in legal_moves.items() if value}

    def test_array(self, test):
        return(test.count(test[0]) == len(test)) & (test[0] != " ")

    def is_game_over(self):

        # Row win
        for i in range(self.rows):
            for j in range(self.columns - self.win_cnt+1):
                test = [self.grid[i][j+k] for k in range(self.win_cnt)]
                if self.test_array(test):
                    self.game_over = True
                    self.players[self.current_player].score = self.win_points
                    return True

        # Column win

        for j in range(self.columns):
            for i in range(self.rows - self.win_cnt+1):
                test = [self.grid[i+k][j] for k in range(self.win_cnt)]
                if self.test_array(test):
                    self.game_over = True
                    return True

        # Down/right diagonal
        for i in range(self.rows - self.win_cnt+1):
            for j in range(self.columns - self.win_cnt+1):
                test = [self.grid[i+k][j+k] for k in range(self.win_cnt)]
                if self.test_array(test):
                    self.game_over = True
                    return True

        # up/right diagonal
        for i in range(self.win_cnt - 1, self.rows):
            for j in range(self.columns - self.win_cnt+1):
                test = [self.grid[i-k][j+k] for k in range(self.win_cnt)]
                if self.test_array(test):
                    self.game_over = True
                    return True

        if not self.get_legal_actions()[0]:
            return True

        return False

    def get_legal_actions(self):
        legal_actions = {}
        act_cnt = 0
        for j in range(self.columns):
            if not all([self.grid[i][j] != " " for i in range(self.rows)]):
                legal_actions[act_cnt] = j
                act_cnt += 1

        if not legal_actions:
            self.game_over = True
        self.legal_actions = legal_actions
        return legal_actions.keys(), self.current_player

    def update_game(self, action):
        sel_action = self.legal_actions[action]
        for i in range(self.rows):
            if self.grid[self.rows - i - 1][sel_action] == " ":
                self.grid[self.rows -
                          i - 1][sel_action] = self.players[self.current_player].mark
                break
        self.current_player = (self.current_player + 1) % self.player_count
        self.is_game_over()
        self.save_state()

    def save_state(self):
        self.state = ""
        for i in range(self.columns):
            self.state += "|".join(self.grid[i][j]
                                   for j in range(self.columns)) + "\n"
            self.state += "_" * (self.columns * 2 - 1) + "\n"

    def play_game(self):
        self.save_state()
        while not self.is_game_over():
            self.get_legal_actions()
            print(self.state)
            print(self.legal_actions)
            action = int(input("Choose an action"))
            self.update_game(action)


# test = Game(2)

# test.play_game()
