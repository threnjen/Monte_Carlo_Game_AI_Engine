# this file is the custom monte carlo framework for our AI to plug into


import numpy as np
import copy
from collections import defaultdict

class TurnEngine():
    
    def __init__(self):
        '''
        Instantiates the game logic and the root monte carlo node
        '''    
        self.logic = Game_Logic()
        self.root = MonteCarlo(state=self.logic._state, parent=None, parent_action=None, legal_actions=self.logic.get_legal_actions()) # instantiate the root node of the game
                                            # initial_state is to be defined by us and sent in here. how to use it? Is intended as board state
        
    def play_game(self, num_sims):
        '''
        Starts the game. Runs a given number of simulations to terminus, according to the Monte Carlo schema:
        1. Find next node to rollout (Expansion)
        2. Rollout game (Simulation)
        3. Backpropogate
        '''
        print("Starting simulation with "+str(num_sims)+" sims")

        for i in range(num_sims): # how many simulations with this initial state?
            
            v = self._tree_policy(self.root) # call TREE_POLICY to select the node to rollout. v is a NODE
            #print("Rollout node: "+str(v))

            # COPY THE GAME STATE HERE AND ROLL OUT ON IT NOT THE REAL GAME
            self.logic_copy = copy.deepcopy(self.logic)

            reward = self.rollout() # call ROLLOUT on the node v. Starts from node v and takes legal actions until the game ends. Gets the rewards
            print("Reward: "+str(reward))

            #print(v)
            self.backpropogate(reward, v) # backpropogates with the reward. Calls BACKPROPOGATE
    
        selected_node = self.root.best_child(c_param=0) # returns the best child node to the main function. Calls BEST_CHILD
        print("Best move is: "+str(selected_node))

        #return # return what?

    def _tree_policy(self, node):
        '''
        Selects node to run rollout. Is looking for the furthest terminal node to roll out.
        '''
        current_node = node

        #while not current_node.is_terminal_node(): # calls a check on if this is a terminal node. Will keep looping until this is true.
            # it's checking for whether this node is already a leaf end, or if it needs to be expanded
        #print("Entering Tree Policy function")
        while not self.logic.is_game_over():

            #print("Game has not ended")
            if not len(current_node._untried_actions)==0: # check if the current node isn't fully expanded
                #print("Current node is not fully expanded, expanding node")
                #return current_node.expand() # if not expanded, expand current node
                #print("Returning a node to the game engine")
                return self.expand(current_node) # if not expanded, expand current node
            else: # if current node is expanded, find best child
                #print("Current node is fully expanded, getting best child")
                current_node = current_node.best_child() # calls BEST_CHILD to get best scoring leaf
        
        #print("Game was over, returning same node to game engine")
        return current_node # if current node got true from is_terminal, returns itself. otherwise returns best child.
    
    def expand(self, current_node):
        '''
        From the present state we expand the nodes to the next possible states
        '''
        action = current_node._untried_actions.pop() # pops off an untried action
        next_state = self.logic.update_game(action) # calls move function on the action to get next_state. Calls MOVE in GAME_LOGIC object
        child_node = MonteCarlo(
                state=next_state, parent=current_node, parent_action=action) # instantiates a new node from next state and the action selected
        current_node.children.append(child_node) # appends this new child node to the current node's list of children
        return child_node

    def rollout(self):
        '''
        On rollout call, the entire game is simulated to terminus and the outcome of the game is returned
        '''
        #print("Now entering rollout function")
        #while not self.logic.is_game_over(): # checks the state for game over boolean and loops if it's false
        while not self.logic_copy.is_game_over(): # checks the state for game over boolean and loops if it's false
            print("Game is not over")

            print("Getting possible moves")
            #possible_moves = self.logic.get_legal_actions() # call to get legal moves. Calls GET_LEGAL_ACTIONS in GAME_LOGIC object
            possible_moves = self.logic_copy.get_legal_actions() # call to get legal moves. Calls GET_LEGAL_ACTIONS in GAME_LOGIC object
            print(possible_moves)

            #action = self.rollout_policy(possible_moves) # Calls ROLLOUT_POLICY in case needs more complicated
            action = possible_moves[np.random.randint(len(possible_moves))] # call random move from possible moves
            print("Picked random action: "+str(action))

            #self.logic.update_game(action) # takes action just pulled at random. Calls MOVE in GAME_LOGIC object
            self.logic_copy.update_game(action) # takes action just pulled at random. Calls MOVE in GAME_LOGIC object
            print("Updating game with move")

        print("Game has ended; returning result")
        #return self.logic.game_result() # returns game_result when game is flagged over. Calls GAME_RESULT in GAME_LOGIC object
        return self.logic_copy.game_result() # returns game_result when game is flagged over. Calls GAME_RESULT in GAME_LOGIC object

    def backpropogate(self, reward, node):
        '''
        all node statistics are updated. Until the parent node is reached.
        All visits +1
        win stats/scores/etc are incrememnted as needed
        '''

        #print("Now entering backpropogation function")
        #print(node.number_of_visits)
        #print(node.results[0])

        node.number_of_visits += 1 # updates self with number of visits
        node.results[reward] +=1 # updates self with reward (sent in from backpropogate)
        #print("Updated self results")

        if node.parent: # if this node has a parent,
            #print("Backpropogating parent node")
            #self.parent.backpropogate(reward) # call backpropogate on the parent, so this will continue until root note which has no parent
            self.backpropogate(reward, node.parent) # call backpropogate on the parent, so this will continue until root note which has no parent


class MonteCarlo():

    def __init__(self, state=None, parent=None, parent_action=None, legal_actions=None):
        self.state = state # board state, in tic tac toe is 3x3 array. (defined by user)
        self.parent = parent # none for the root node and for other nodes is = node derived from. First turn will be none
        self.parent_action = parent_action # none for root but is = parent action for other nodes
        self.children = [] # all possible actions from current node
        self.number_of_visits = 0 # number of times current node is visited
        self.results = defaultdict(int) 
        self.results[1] = 0 # in this tic tac toe example, this is the win counter
        self.results[-1] = 0 # in this tic tac toe example, this is the loss counter
        self._untried_actions = None
        self._untried_actions = legal_actions # call to get legal moves. Calls GET_LEGAL_ACTIONS in GAME_LOGIC object
        return

    def node_score(self):
        '''
        returns diff of wins and losses
        '''
        wins = self.results[1]
        losses = self.results[-1]
        return wins - losses

    def node_visits(self):
        # returns number of times that node has been visited
        return self.number_of_visits

    def best_child(self, c_param=2):
        '''
        selects best child node from available array
        first param is exploitation and second is exploration
        '''
        #print("Now in best_child function")
        # makes an array of the leaf calculations
        choices_weights = [(c.node_score() / c.node_visits()) + c_param * np.sqrt((np.log(self.node_visits())) / c.node_visits()) for c in self.children] 
                        #calculates scores for child nodes
        return self.children[np.argmax(choices_weights)] # gets index of max score and sends back identity of child


class Game_Logic():

    def __init__(self):
        '''
        declare game state
        '''
        self.game = SimpleArrayGame()
        self._state = self.game._state
    
    def update_game(self, action):
        '''
        Modify according to your game or 
        needs. 
        '''
        return self.game.update_game(action)
        #self._state[action] = 1
        #return self._state

    def get_legal_actions(self):
        '''
        report on currently available actions after checking board space
        '''
        return self.game.get_legal_actions()
        #return [i for i in range(len(self._state)) if self._state[i] == 0]

    def is_game_over(self):
        '''
        Modify according to your game or 
        needs. It is the game over condition
        and depends on your game. Returns
        true or false
        '''
        return self.game.is_game_over()
        #return np.where(self._state == 1)[0].size > 0

    def game_result(self):
        '''
        Returns 1 or 0 or -1 depending
        on your state corresponding to win,
            tie or a loss.
        '''
        return self.game.game_result()  

class SimpleArrayGame():
    
    def __init__(self):
        self._state = np.array([0,0,0])

    def update_game(self, action):
        '''
        Modify according to your game or 
        needs. 
        '''
        self._state[action] = 1
        return self._state

    def get_legal_actions(self):
        '''
        report on currently available actions after checking board space
        '''
        return [i for i in range(len(self._state)) if self._state[i] == 0]

    def is_game_over(self):
        '''
        Modify according to your game or 
        needs. It is the game over condition
        and depends on your game. Returns
        true or false
        '''
        return np.count_nonzero(self._state) > 1
    
    def game_result(self):
        '''
        Returns 1 or 0 or -1 depending
        on your state corresponding to win,
            tie or a loss.
        '''
        if self._state[0]==1:         
            print("Score is 1")
            return 1
        if self._state[1]==1:
            print("Score is -1")
            return -1
        if self._state[2]==1:
            print("Score is 0")
            return 0    

game = TurnEngine()
game.play_game(100)







    #def rollout_policy(self, possible_moves):
    #    '''
    #    randomly selects a move out of possible moves and returns the random move
    #    unused in current game logic
    #    '''
    #    return possible_moves[np.random.randint(len(possible_moves))]

    #selected_node = self.root.best_action(num_sims) # call BEST_ACTION, get the best node for the root node to move to

    #def best_action(self, num_sims):
    #    '''
    #    Returns the node corresponding to the best possible move
    #    Carries out expansion, simulation and backpropogation
    #    '''
    #    simulation_no = num_sims 

    #    for i in range(num_sims): # how many simulations with this initial state?

    #        v = self._tree_policy() # call TREE_POLICY to select the node to rollout. v is a NODE
    #        reward = v.rollout() # call ROLLOUT on the node v. Starts from node v and takes legal actions until the game ends. Gets the rewards
    #        v.backpropogate(reward) # backpropogates with the reward. Calls BACKPROPOGATE
    
    #    return self.best_child(c_param=0) # returns the best child node to the main function. Calls BEST_CHILD

    #def is_terminal_node(self):
    #    return self.logic.is_game_over() # checks is_game_over for boolean. Calls IS_GAME_OVER (defined by user)
    #    #return False    

    #def expand(self):
    #    '''
    #    From the present state we expand the nodes to the next possible states
    #    '''
    #    action = self._untried_actions.pop() # pops off an untried action
    #    next_state = self.logic.move(action) # calls move function on the action to get next_state. Calls MOVE in GAME_LOGIC object
    #    child_node = MonteCarlo(
    #            state=next_state, parent=self, parent_action=action) # instantiates a new node from next state and the action selected
    #    self.children.append(child_node) # appends this new child node to the current node's list of children
    #    return child_node

    #def rollout(self):
    #    '''
    #    On rollout call, the entire game is simulated to terminus and the outcome of the game is returned
    #    '''
        #current_rollout_state = self.state # gets the current board state

        #while not current_rollout_state.is_game_over(): # checks the state for game over boolean and loops if it's false

            #possible_moves = self.logic.get_legal_actions() # call to get legal moves. Calls GET_LEGAL_ACTIONS in GAME_LOGIC object

            #action = self.rollout_policy(possible_moves) # Calls ROLLOUT_POLICY in case needs more complicated
            #action = possible_moves[np.random.randint(len(possible_moves))] # call random move from possible moves

            #self.logic.move(action) # takes action just pulled at random. Calls MOVE in GAME_LOGIC object
    
        #return self.logic.game_result() # returns game_result when game is flagged over. Calls GAME_RESULT in GAME_LOGIC object