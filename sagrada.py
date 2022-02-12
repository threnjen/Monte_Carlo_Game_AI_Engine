from turtle import pos
import numpy as np
import random
import copy
from colorama import init, Fore, Back, Style

# Initializes Colorama
init(autoreset=True)

class Board():

    def __init__(self):
        self.board ={}
        for i in range(4):
            for j in range(5):
                self.board[(i,j)] = '  '  
    
        self.adjacency = {}
        self.adjacency[0,0] = [(0,1), (1,0)]
        self.adjacency[0,1] = [(0,0), (0,2), (1,1)]
        self.adjacency[0,2] = [(0,1), (0,3), (1,2)]
        self.adjacency[0,3] = [(0,2), (0,4), (1,3)]
        self.adjacency[0,4] = [(0,3), (1,4)]
        self.adjacency[1,0] = [(0,0), (1,1), (2,0)]
        self.adjacency[1,1] = [(1,0), (0,1), (1,2), (2,1)]
        self.adjacency[1,2] = [(1,1), (0,2), (1,3), (2,2)]
        self.adjacency[1,3] = [(1,2), (0,3), (1,4), (2,3)]
        self.adjacency[1,4] = [(0,4), (1,3), (2,4)]
        self.adjacency[2,0] = [(1,0), (2,1), (3,0)]
        self.adjacency[2,1] = [(2,0), (1,1), (2,2), (3,1)]
        self.adjacency[2,2] = [(2,1), (1,2), (2,3), (3,2)]
        self.adjacency[2,3] = [(2,2), (1,3), (2,4), (3,3)]
        self.adjacency[2,4] = [(2,3), (1,4), (3,4)]
        self.adjacency[3,0] = [(2,0), (3,1)]
        self.adjacency[3,1] = [(3,0), (2,1), (3,2)]
        self.adjacency[3,2] = [(3,1), (2,2), (3,3)]
        self.adjacency[3,3] = [(3,2), (2,3), (3,4)]
        self.adjacency[3,4] = [(3,3), (2,4)]

class Player():

    def __init__(self, player_board, scorer):
        self.player = Board()      
        self.map_reference = player_board[0]
        self.tokens = player_board[1]
        self.score_color = scorer
        print(self.score_color, self.tokens)
        self.draw_player_board()
        self._state = self.draw_player_board()
        self.first_turn = True
    
    def draw_player_board(self):
        self.player_board  = f"""\n
        Player Board\t\t\tReference Map\n
        ________________\t\t\t___________
        |{self.player.board[0,0]}|{self.player.board[0,1]}|{self.player.board[0,2]}|{self.player.board[0,3]}|{self.player.board[0,4]}|\t\t\t|{self.map_reference[0,0]}|{self.map_reference[0,1]}|{self.map_reference[0,2]}|{self.map_reference[0,3]}|{self.map_reference[0,4]}|          
        ________________\t\t\t___________
        |{self.player.board[1,0]}|{self.player.board[1,1]}|{self.player.board[1,2]}|{self.player.board[1,3]}|{self.player.board[1,4]}|\t\t\t|{self.map_reference[1,0]}|{self.map_reference[1,1]}|{self.map_reference[1,2]}|{self.map_reference[1,3]}|{self.map_reference[1,4]}|
        ________________\t\t\t___________
        |{self.player.board[2,0]}|{self.player.board[2,1]}|{self.player.board[2,2]}|{self.player.board[2,3]}|{self.player.board[2,4]}|\t\t\t|{self.map_reference[2,0]}|{self.map_reference[2,1]}|{self.map_reference[2,2]}|{self.map_reference[2,3]}|{self.map_reference[2,4]}|
        ________________\t\t\t___________
        |{self.player.board[3,0]}|{self.player.board[3,1]}|{self.player.board[3,2]}|{self.player.board[3,3]}|{self.player.board[3,4]}|\t\t\t|{self.map_reference[3,0]}|{self.map_reference[3,1]}|{self.map_reference[3,2]}|{self.map_reference[3,3]}|{self.map_reference[3,4]}|
        ________________\t\t\t___________
        """
        print(self.player_board)

    def check_legal_positions(self, die):
        print(die)

        self.color, self.number = die[0][:1], int(die[1])

        legal_positions = []

        if self.first_turn:
            for i in range(self.map_reference.shape[0]):
                for j in range(self.map_reference.shape[1]):
                    if self.map_reference[i,j] == ' ':
                        legal_positions.append((i,j))
                    elif self.map_reference[i,j].lower().isdigit() and int(self.map_reference[i,j])==self.number:
                        legal_positions.append((i,j))
                    elif self.map_reference[i,j].lower().isalpha() and self.map_reference[i,j].lower()==self.color:
                        legal_positions.append((i,j))
                    else:
                        continue
            self.first_turn=False
            return legal_positions

        
        occupied = [k for (k,v) in self.player.board.items() if v != '  ']
        print(occupied)



        

        for i in range(self.map_reference.shape[0]):
            for j in range(self.map_reference.shape[1]):
                if self.map_reference[i,j] == ' ':
                    legal_positions.append((i,j))
                elif self.map_reference[i,j].lower().isdigit() and int(self.map_reference[i,j])==self.number:
                    legal_positions.append((i,j))
                elif self.map_reference[i,j].lower().isalpha() and self.map_reference[i,j].lower()==self.color:
                    legal_positions.append((i,j))
                else:
                    continue


        for spot in legal_positions.copy():
            if self.player.board[spot] != '  ':
                print(self.player.board[spot])
                legal_positions.remove(spot)

        if len(legal_positions) == 0:
            legal_positions.append('None')

        return legal_positions

    def update_board(self, position):
        print(f'position returned is {position}')

        if position != 'None':
            self.player.board[position] = f'{self.color}{self.number}'

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
    '''Public scoring cards for end game scoring'''
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
        random.seed(random.randint(1,1000000))
        self.num_players = players
        self.game_over = False
        self.name = "sagrada"
        self._state = ""
        self.scores = {n:0 for n in range(players)}
        self.current_player_num = 0
        self.round_start_player = 0
        self.round = 1
        self.game_dice = DiceHolder(self.num_players)
        self.boards = Player_Boards()
        self.players = {n:Player(self.boards.get_board_map(), self.boards.get_special_scorer()) for n in range(players)}
        self.flag = 'draw'
        self.new_round()

    def new_round(self):
        print(f"Round {self.round}")
        self.round_draw = self.game_dice.refill_supply()

        self.turn_order = []

        self.turn_order.append(self.round_start_player)

        next_player_num = self.round_start_player
        for i in range(self.num_players - 1):
            self.turn_order.append((next_player_num + 1) % self.num_players)
            next_player_num = (next_player_num + 1) % self.num_players
        self.turn_order += self.turn_order[::-1]

        self.current_player_num = self.turn_order[0]
        print(self.turn_order)
    
    def get_legal_actions(self):
        '''Hook #1 Sends legal actions in
        Format [[list of legal actions], active player ID]'''

        if self.flag == 'draw':
            print("getting draw actions")
            self.players[self.current_player_num].draw_player_board()
            self.legal_actions = (self.round_draw, self.current_player_num)
            return self.legal_actions
        
        if self.flag == 'place':
            print("getting place actions")
            self.legal_positions = self.players[self.current_player_num].check_legal_positions(self.die)
            self.legal_actions = (self.legal_positions, self.current_player_num)
            return self.legal_actions            
    
    def update_game(self, action, player):
        """Hook #2
            action (list item): selected item from list of legal actions
            player (int): player number""" 
 
        if len(self.round_draw) == 1:
            self.round += 1
            self.new_round()
            self.round_start_player = (self.round_start_player + 1) % self.num_players 

        if self.round > 10:
            self.game_over = True
            print("Game is over")

        if self.flag == 'draw':
            print("Update game: drawing")
            self.die = self.round_draw[action]
            del self.round_draw[action] 
            self.flag = 'place'     
            
        else:
            print("Update game: placing")
            # Do player board stuff here! 
            action = self.legal_positions[action]
            print("Do player board stuff here")
            self.players[self.current_player_num].update_board(action)
            self.current_player_num = self.turn_order[(self.num_players*2) - len(self.round_draw)+1]
            print(f"Just updated current player to {self.current_player_num}")
            self.flag = 'draw'

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

            print("requesting actions")
            actions, player = game.get_legal_actions()
            print(actions, player)
            action = int(input(f"Enter action as index 0-{len(actions)-1}: "))
            print("update game")
            game.update_game(action, player)

game = Play(3)

#game = Game(2)