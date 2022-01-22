import numpy as np

class SimpleArrayGame():
    '''
    Game rules:
    There is an array of 5x5 zeros
    Each round, the player puts a 1 in a specific slot of the array
    When any column sums to 5, the game is over
    The score is the index of the column that was filled
    
    '''

    def __init__(self):
        self._state = np.zeros((5, 5))

    def update_game(self, action):
        '''
        Modify according to your game or 
        needs. 
        '''
        action = tuple(action)
        self._state[action] = 1
        return self._state

    def get_legal_actions(self):
        '''
        report on currently available actions after checking board space
        '''
        #return [i for i in range(len(self._state)) if self._state[i] == 0]
        return list(np.argwhere(self._state == 0))

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
        Returns 1 or 0 or -1 depending
        on your state corresponding to win,
            tie or a loss.
        '''
        finished_array = self._state.sum(axis=0)
        return np.argmax(finished_array)