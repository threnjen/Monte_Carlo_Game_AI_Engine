import numpy as np
from games.game_class import Game

class SimpleArrayGame(Game):
    '''
    Game rules:
    There is an array of 5x5 zeros
    Each round, the player puts a 1 in a specific slot of the array
    When any column sums to 5, the game is over
    The score is the index of the column that was filled
    
    '''

    def __init__(self, players):
        self._state = np.zeros((5, 5))
        self.name = "array_test"

    def update_game(self, action, player):
        '''
        Modify according to your game or 
        needs. 
        '''
        #action = tuple(action)
        self._state[action] = 1
        return self._state

    def get_legal_actions(self, policy=False):
        '''
        report on currently available actions after checking board space
        '''
        #return [i for i in range(len(self._state)) if self._state[i] == 0]
        #return [list(np.argwhere(self._state == 0)), 0]
        return [list([tuple(i) for i in (np.argwhere(self._state == 0))]), 0]
        

    def is_game_over(self):
        '''
        Modify according to your game or 
        needs. It is the game over condition
        and depends on your game. Returns
        true or false
        '''
        return np.any(self._state.sum(axis=0)==5)
    
    def game_result(self):
        '''
        Returns a score which correlated to the column, so rightmost column scores highest
        '''
        scores = {}
        finished_array = self._state.sum(axis=0)
        scores[0] = np.argmax(finished_array)
        return scores

    def draw_board(self):

        return self._state