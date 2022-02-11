import numpy as np
import random

class Player():

    def __init__(self, player_board):
        self.board = np.zeros((4,5))
        self.map_reference = player_board
        self._state = None
        self.draw_board()
        print(self.board)
        #print(self.map_reference)
        #print(self.map_reference[0,2]) # expect r,''
        #print(self.map_reference[2,0]) # expect b,''
        #print(self.map_reference[2,4]) # expect '', 5
        print(self._state)
    
    def draw_board(self):
        """Just draw an ASCII board.
        """
        self._state = f"""\n
        _____________________________________________
        |{self.map_reference[0,0]}|{self.map_reference[0,1]}|{self.map_reference[0,2]}|{self.map_reference[0,3]}|{self.map_reference[0,4]}|          
        _____________________________________________
        |{self.map_reference[1,0]}|{self.map_reference[1,1]}|{self.map_reference[1,2]}|{self.map_reference[1,3]}|{self.map_reference[1,4]}|  
        _____________________________________________
        |{self.map_reference[2,0]}|{self.map_reference[2,1]}|{self.map_reference[2,2]}|{self.map_reference[2,3]}|{self.map_reference[2,4]}|  
        _____________________________________________
        |{self.map_reference[3,0]}|{self.map_reference[3,1]}|{self.map_reference[3,2]}|{self.map_reference[3,3]}|{self.map_reference[3,4]}|
        _____________________________________________
        """

class Game():

    def __init__(self, players):
        self.game_over = False
        self._state = ""
        #self.draw_board()
        self.scores = {n:0 for n in range(players)}
        self.current_player_num = 0
        self.name = "sagrada"

        self.board_maps = {
            'Fulgor del Cielo': np.array([
                                [['',''],['B',''],['R',''],['',''],['','']],
                                [['',''],['','4'],['','5'],['',''],['B','']],
                                [['B',''],['','2'],['',''],['R',''],['','5']],
                                [['','6'],['R',''],['','3'],['','1'],['','']]
            ])                 
        }

        self.players = {n:Player(self.get_board_map()) for n in range(players)}

        
     
    
    def get_board_map(self):
        
        get_board = random.choice(list(self.board_maps.keys()))
        player_map = self.board_maps[get_board]
        del self.board_maps[get_board]
        return player_map

    
        
        

game = Game(1)