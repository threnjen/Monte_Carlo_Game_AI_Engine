import numpy as np
import random

class Player():

    def __init__(self, player_board, scorer):
        self.board = np.zeros((4,5))
        self.map_reference = player_board[0]
        self.tokens = player_board[1]
        self._state = None
        self.score_color = scorer
        print(self.score_color, self.tokens)
        self.draw_board()
        print(self.board)
        print(self._state)
    
    def draw_board(self):
        """Just draw an ASCII board.
        """
        self._state = f"""\n
        ___________
        |{self.map_reference[0,0]}|{self.map_reference[0,1]}|{self.map_reference[0,2]}|{self.map_reference[0,3]}|{self.map_reference[0,4]}|          
        ___________
        |{self.map_reference[1,0]}|{self.map_reference[1,1]}|{self.map_reference[1,2]}|{self.map_reference[1,3]}|{self.map_reference[1,4]}|  
        ___________
        |{self.map_reference[2,0]}|{self.map_reference[2,1]}|{self.map_reference[2,2]}|{self.map_reference[2,3]}|{self.map_reference[2,4]}|  
        ___________
        |{self.map_reference[3,0]}|{self.map_reference[3,1]}|{self.map_reference[3,2]}|{self.map_reference[3,3]}|{self.map_reference[3,4]}|
        ___________
        """

class DiceHolder():

    def __init__(self, players):
        self.num_round_dice = players*2 + 1
        self.master_dice_dictionary = {'red':18, 'yellow':18, 'green':18, 'blue':18, 'purple':18}

    def refill_supply(self):
        self.draw_dice_dictionary = {'red':0, 'yellow':0, 'green':0, 'blue':0, 'purple':0}

        self.draw_dice_choice = []

        for i in range(self.num_round_dice):
            draw = random.choice(list(self.master_dice_dictionary))
            self.master_dice_dictionary[draw] -= 1
            if self.master_dice_dictionary[draw]==0: del(draw)
            self.draw_dice_choice.append([draw, random.randint(1,6)])
        return self.draw_dice_choice


class Public_Scorers():
    def __init__(self):
        pass

class Player_Boards():

    def __init__(self):
        self.board_maps = {
            'Fulgor del Cielo 1': [np.array([
                                [' ','B','R',' ',' '],
                                [' ','4','5',' ','B'],
                                ['B','2',' ','R','5'],
                                ['6','R','3','1',' ']]) , 5],
            'Fulgor del Cielo 2': [np.array([
                                [' ','B','R',' ',' '],
                                [' ','4','5',' ','B'],
                                ['B','2',' ','R','5'],
                                ['6','R','3','1',' ']]) , 5],
            'Fulgor del Cielo 3': [np.array([
                                [' ','B','R',' ',' '],
                                [' ','4','5',' ','B'],
                                ['B','2',' ','R','5'],
                                ['6','R','3','1',' ']]) , 5],
                             }
        
        self.special_scorer = ['red', 'yellow', 'green', 'purple', 'blue']
    
    def get_board_map(self):
        get_board = random.choice(list(self.board_maps.keys()))
        player_map = self.board_maps[get_board]
        del self.board_maps[get_board]
        return player_map
    
    def get_special_scorer(self):
        choice = random.choice(self.special_scorer)
        self.special_scorer.remove(choice)
        return choice


class Game():

    
    def __init__(self, players):
        self.num_players = players
        self.game_over = False
        self.name = "sagrada"
        self._state = ""
        self.scores = {n:0 for n in range(players)}
        self.current_player_num = 0
        self.round = 1
        self.game_dice = DiceHolder(self.num_players)
        self.boards = Player_Boards()
        self.players = {n:Player(self.boards.get_board_map(), self.boards.get_special_scorer()) for n in range(players)}
        self.new_round()

    def new_round(self):

        print(f"Round {self.round}")
        self.round_draw = self.game_dice.refill_supply()


    
    def get_legal_actions(self):
        '''Hook #1 Sends legal actions in
        Format [[list of legal actions], active player ID]'''

        self.legal_actions = self.round_draw
        return(self.legal_actions, self.current_player_num)


    
    def update_game(self, action, player):
        """Hook #2
            action (list item): selected item from list of legal actions
            player (int): player number
        """        
        self.round_draw.remove(action)

        # Do player board stuff here

        self.current_player_num = player%self.num_players

        if len(self.round_draw) == 1:
            self.round += 1
            self.new_round()

        if self.round > 10:
            self.game_over = True
            print("Game is over")


    
    def is_game_over(self):
        """ Hook #3 Checks if game has ended

        Returns:
            [True/False]: True/False if game is over
        """        
        return self.game_over


    
    def game_result(self):
        pass
        """ Hook #4 Retrieves game score

        Must be a dictionary in format {playerID: Score}
        Where playerID matches IDs sent with get_legal_actions
        """        

    
class Play():

    def __init__(self, players):

        game = Game(players)

        while game.game_over == False:

            actions, player = game.get_legal_actions()
            print(actions)
            action = actions[int(input(f"Enter action as index 0-{len(actions)-1}: "))]

            game.update_game(action, player)



game = Play(2)

#game = Game(2)