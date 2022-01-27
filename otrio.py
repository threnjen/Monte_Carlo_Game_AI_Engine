import numpy as np

class Player():


    def __init__(self, mark, id):

        self.mark = mark
        self.id = id

        self.pieces = {}
        self.pieces[0] = [mark,mark,mark]
        self.pieces[1] = [mark,mark,mark]
        self.pieces[2] = [mark,mark,mark]

class Game():

    def __init__(self, players):

        print("Initializing board...")
        self.board = np.zeros((3,3,3)).astype('int')
        self.game_over = False
        self._state = ""
        self.draw_board()
        self.scores = {n+1:0 for n in range(players)}
        self.current_player_num = 1
        self.name = "Otrio"

        if players >= 2:
            self.players = {1: Player(1, 1), 2: Player(2, 2)}
        if players >= 3:
            self.players[3] = Player(3, 3)
        if players == 4:
            self.players[4] = Player(4, 4)
        if players <2 or players >4:
            print("Invalid player number selection. Must enter players from 2-4")

        self.player_count = players

        print("Setting up win conditions")
        self.win_conditions = {

            "Level 1 top_row":[[0,0,0], [0,0,1], [0,0,2]],
            "Level 1 mid_row":[[0,1,0], [0,1,1], [0,1,2]],
            "Level 1 bot_row":[[0,2,0], [0,2,1], [0,2,2]],
            "Level 1 left_col":[[0,0,0],[0,1,0], [0,2,0]],
            "Level 1 mid_col":[[0,0,1], [0,1,1], [0,1,2]],
            "Level 1 right_col":[[0,0,2], [0,1,2], [0,2,2]],
            "Level 1 left_diag":[[0,0,0], [0,1,1], [0,2,2]],
            "Level 1 right_diag":[[0,0,2], [0,1,1], [0,2,0]],

            "Level 2 top_row":[[1,0,0], [1,0,1], [1,0,2]],
            "Level 2 mid_row":[[1,1,0], [1,1,1], [1,1,2]],
            "Level 2 bot_row":[[1,2,0], [1,2,1], [1,2,2]],
            "Level 2 left_col":[[1,0,0], [1,1,0], [1,2,0]],
            "Level 2 mid_col":[[1,0,1], [1,1,1], [1,2,1]],
            "Level 2 right_col":[[1,0,2], [1,1,2], [1,2,2]],
            "Level 2 left_diag":[[1,0,0], [1,1,1], [1,2,2]],
            "Level 2 right_diag":[[1,0,2], [1,1,1], [1,2,0]],
            
            "Level 3 top_row":[[2,0,0], [2,0,1], [2,0,2]],
            "Level 3 mid_row":[[2,1,0], [2,1,1], [2,1,2]],
            "Level 3 bot_row":[[2,2,0], [2,2,1], [2,2,2]],
            "Level 3 left_col":[[2,0,0], [2,1,0], [2,2,0]],
            "Level 3 mid_col":[[2,0,1], [2,1,1], [2,2,1]],
            "Level 3 right_col":[[2,0,2], [2,1,2], [2,2,2]],
            "Level 3 left_diag":[[2,0,0], [2,1,1], [2,2,2]],
            "Level 3 right_diag":[[2,0,2], [2,1,1], [2,2,0]],

            "Single Column 0,0":[[0,0,0], [1,0,0], [2,0,0]],
            "Single Column 0,1":[[0,0,1], [1,0,1], [2,0,1]],
            "Single Column 0,2":[[0,0,2], [1,0,2], [2,0,2]],
            "Single Column 1,0":[[0,1,0], [1,1,0], [2,1,0]],
            "Single Column 1,1":[[0,1,1], [1,1,1], [2,1,1]],
            "Single Column 1,2":[[0,1,2], [1,1,2], [2,1,2]],
            "Single Column 2,0":[[0,2,0], [1,2,0], [2,2,0]],
            "Single Column 2,1":[[0,2,1], [1,2,1], [2,2,1]],
            "Single Column 2,2":[[0,2,2], [1,2,2], [2,2,2]],

            "Diag top_row asc":[[0,0,0], [1,0,1], [2,0,2]],
            "Diag top_row desc":[[2,0,0], [1,0,1], [0,0,2]],
            "Diag mid_row asc":[[0,1,0], [1,1,1], [2,1,2]],
            "Diag mid_row desc":[[2,1,0], [1,1,1], [0,0,2]],
            "Diag bot_row asc":[[0,2,0], [1,2,1], [2,2,2]],
            "Diag bot_row desc":[[2,2,0], [1,2,1], [0,2,2]],
            "Diag left_col asc":[[0,0,0], [1,1,0], [2,2,0]],
            "Diag left_col desc":[[0,2,0], [1,1,0], [2,0,0]],
            "Diag mid_col asc":[[0,0,1], [1,1,1], [2,2,1]],
            "Diag mid_col desc":[[0,2,1], [1,1,1], [2,0,1]],
            "Diag right_col asc":[[0,0,2], [1,1,2], [2,2,2]],
            "Diag right_col desc":[[2,2,2], [1,1,2], [0,0,2]],
            "Diag left_diag asc":[[0,0,0], [1,1,1], [2,2,2]],
            "Diag right_diag asc":[[2,0,0], [1,1,1], [0,2,2]],
            "Diag left_diag desc":[[0,2,0], [1,1,1], [2,0,2]],
            "Diag right_diag desc":[[2,2,0], [1,1,1], [0,0,2]],

                }
        
        self.win_array = list(self.win_conditions.values())

    def draw_board(self):

        self._state = f"""
        Level 1\t\t\tLevel 2\t\t\tLevel 3\n
        {self.board[0,0,0]}|{self.board[0,0,1]}|{self.board[0,0,2]}\t\t\t{self.board[1,0,0]}|{self.board[1,0,1]}|{self.board[1,0,2]}\t\t\t{self.board[2,0,0]}|{self.board[2,0,1]}|{self.board[2,0,2]}       
        _____\t\t\t_____\t\t\t_____
        {self.board[0,1,0]}|{self.board[0,1,1]}|{self.board[0,1,2]}\t\t\t{self.board[1,1,0]}|{self.board[1,1,1]}|{self.board[1,1,2]}\t\t\t{self.board[2,1,0]}|{self.board[2,1,1]}|{self.board[2,1,2]}
        _____\t\t\t_____\t\t\t_____
        {self.board[0,2,0]}|{self.board[0,2,1]}|{self.board[0,2,2]}\t\t\t{self.board[1,2,0]}|{self.board[1,2,1]}|{self.board[1,2,2]}\t\t\t{self.board[2,2,0]}|{self.board[2,2,1]}|{self.board[2,2,2]}
        """

    def make_move(self, action, current_player_num):

        
        position = tuple(action)

        player_mark = self.players[current_player_num].pieces[action[0]].pop()

        self.board[position] = player_mark
        self.draw_board()

        if self.current_player_num == max(self.scores.keys()):
            self.current_player_num = 1
        else:
            self.current_player_num += 1
        
        #self.current_player_num = (
        #    self.current_player_num + 1) % self.player_count + 1


    def get_legal_actions(self):

        current_player = self.current_player_num

        invalid_player_levels = [k for k,v in self.players[current_player].pieces.items() if len(v)==0]

        legal_actions = np.argwhere(self.board == 0).tolist()
        legal_actions = [x for x in legal_actions if x[0] not in invalid_player_levels]

        return [legal_actions, self.current_player_num]        

    
    def update_game(self, action, player):

        self.make_move(action, player)

    
    def is_game_over(self):

        avail_actions = self.get_legal_actions()[0]

        remove_conditions = []

        for single_win_condition in self.win_array:

            test_indices = [tuple(x) for x in single_win_condition] 
            test_win_contents = [self.board[i] for i in test_indices]
        
            if 0 not in test_win_contents and not all(element == test_win_contents[0] for element in test_win_contents):
                remove_conditions.append(single_win_condition)
            elif 0 not in test_win_contents and all(element == test_win_contents[0] for element in test_win_contents):
                player_winner = test_win_contents[0]
                self.scores[player_winner] = 10
                for k in self.scores.keys():
                    if k != player_winner:
                        self.scores[k] = -10
                return True
            else:
                continue

        for i in remove_conditions:
            self.win_array.remove(i)
        
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
    

#game = Game(4)
#game.play_game()
