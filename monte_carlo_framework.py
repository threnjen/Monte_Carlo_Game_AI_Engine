# this file is the custom monte carlo framework for our AI to plug into


import numpy as np
from collections import defaultdict

# wi = number of wins after the i-th move, or total score if using score
# ni = number of simulations for the i-th node
# c = exploration parameter (theoretically equal to √2)
# t = total number of simulations for the parent node

class MonteCarloTreeSearchNode():

    def __init__(self, state=None, parent=None, parent_action=None):
        if state == None:
            self.board = Game_Logic()
            self.state = self.board._state # board state, in tic tac toe is 3x3 array. (defined by user)
        else:
            self.state = state
        self.parent = parent # none for the root node and for other nodes is = node derived from. First turn will be none
        self.parent_action = parent_action # none for root but is = parent action for other nodes
        self.children = [] # all possible actions from current node
        self.number_of_visits = 0 # number of times current node is visited
        self._results = defaultdict(int) 
        self._results[1] = 0 # in this tic tac toe example, this is the win counter
        self._results[-1] = 0 # in this tic tac toe example, this is the loss counter
        self._untried_actions = None
        self._untried_actions = self.board.get_legal_actions() # call to get legal moves. Calls GET_LEGAL_ACTIONS in GAME_LOGIC object
        return
  
    def start(self, num_sims):
        self.root = MonteCarloTreeSearchNode() # instantiate the root node of the game
                                            # initial_state is to be defined by us and sent in here. how to use it? Is intended as board state
        selected_node = self.root.best_action(num_sims) # call BEST_ACTION, get the best node for the root node to move to
        return # return what?

    def expand(self):
        '''
        From the present state we expand the nodes to the next possible states
        '''
        action = self._untried_actions.pop() # pops off an untried action
        next_state = self.board.move(action) # calls move function on the action to get next_state. Calls MOVE in GAME_LOGIC object
        child_node = MonteCarloTreeSearchNode(
                state=next_state, parent=self, parent_action=action) # instantiates a new node from next state and the action selected
        self.children.append(child_node) # appends this new child node to the current node's list of children
        return child_node

    def node_score(self):
        '''
        returns diff of wins and losses
        '''
        wins = self._results[1]
        losses = self._results[-1]
        return wins - losses

    def node_visits(self):
        # returns number of times that node has been visited
        return self._number_of_visits

    def best_child(self, c_param=.1):
        '''
        selects best child node from available array
        first param is exploitation and second is exploration
        '''
        # makes an array of the leaf calculations
        choices_weights = [(c.node_score() / c.node_visits()) + c_param * np.sqrt((np.log(self.node_visits())) / c.node_visits()) for c in self.children] 
                        #calculates scores for child nodes
        return self.children[np.argmax(choices_weights)] # gets index of max score and sends back identity of child

    #def rollout_policy(self, possible_moves):
    #    '''
    #    randomly selects a move out of possible moves and returns the random move
    #    unused in current game logic
    #    '''
    #    return possible_moves[np.random.randint(len(possible_moves))]

    def _tree_policy(self):
        '''
        Selects node to run rollout. Is looking for the furthest terminal node to roll out.
        '''
        current_node = self

        while not self.board.is_game_over(): # calls a check on if this is a terminal node. Will keep looping until this is true.
            # it's checking for whether this node is already a leaf end, or if it needs to be expanded

            if not len(self._untried_actions)==0: # check if the current node isn't fully expanded
                return current_node.expand() # if not expanded, expand current node
            else: # if current node is expanded, find best child
                current_node = current_node.best_child() # calls BEST_CHILD to get best scoring leaf

        return current_node # if current node got true from is_terminal, returns itself. otherwise returns best child.

    def rollout(self):
        '''
        On rollout call, the entire game is simulated to terminus and the outcome of the game is returned
        '''
        while not self.board.is_game_over(): # checks the state for game over boolean and loops if it's false in GAME_LOGIC object

            possible_moves = self.board.get_legal_actions() # call to get legal moves. Calls GET_LEGAL_ACTIONS in GAME_LOGIC object

            #action = self.rollout_policy(possible_moves) # Calls ROLLOUT_POLICY in case needs more complicated
            action = possible_moves[np.random.randint(len(possible_moves))] # call random move from possible moves

            self.board.move(action) # takes action just pulled at random. Calls MOVE in GAME_LOGIC object
    
        return self.board.game_result() # returns game_result when game is flagged over. Calls GAME_RESULT in GAME_LOGIC object

    def backpropogate(self, reward):
        '''
        all node statistics are updated. Until the parent node is reached.
        All visits +1
        win stats/scores/etc are incrememnted as needed
        '''
        self._number_of_visits += 1 # updates self with number of visits
        self._results[reward] +=1 # updates self with reward (sent in from backpropogate)
        if self.parent: # if this node has a parent,
            self.parent.backpropogate(reward) # call backpropogate on the parent, so this will continue until root note which has no parent

    def best_action(self, num_sims):
        '''
        Returns the node corresponding to the best possible move
        Carries out expansion, simulation and backpropogation
        '''
        simulation_no = num_sims # how many simulations with this initial state?

        for i in range(simulation_no):

            v = self._tree_policy() # call TREE_POLICY to select the node to rollout. v is a NODE
            reward = v.rollout() # call ROLLOUT on the node v. Starts from node v and takes legal actions until the game ends. Gets the rewards
            v.backpropogate(reward) # backpropogates with the reward. Calls BACKPROPOGATE
    
        return self.best_child(c_param=0) # returns the best child node to the main function. Calls BEST_CHILD

class Game_Logic():

    def __init__(self):
        '''
        declare game board
        '''
        self._state = np.array([0,0,0])
    
    def move(self, action):
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
        return np.where(self._state == 1)[0].size > 0

    def game_result(self):
        '''
        Returns 1 or 0 or -1 depending
        on your state corresponding to win,
            tie or a loss.
        '''
        if self.state[0]==1:
            return 1
        if self.state[1]==1:
            return -1
        if self.state[2]==2:
            return 0    


        

game = MonteCarloTreeSearchNode()
num_sims = 100
game.start(num_sims)