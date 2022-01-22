import numpy as np
from collections import defaultdict

# wi = number of wins after the i-th move, or total score if using score
# ni = number of simulations for the i-th node
# c = exploration parameter (theoretically equal to √2)
# t = total number of simulations for the parent node

class MonteCarloTreeSearchNode():

    def __init__(self, state, parent=None, parent_action=None):
        self.state = state # board state, in tic tac toe is 3x3 array. (defined by user)
        self.parent = parent # none for the root node and for other nodes is = node derived from. First turn will be none
        self.parent_action = parent_action # none for root but is = parent action for other nodes
        self.children = [] # all possible actions from current node
        self.number_of_visits = 0 # number of times current node is visited
        self._results = defaultdict(int) 
        self._results[1] = 0 # in this tic tac toe example, this is the win counter
        self._results[-1] = 0 # in this tic tac toe example, this is the loss counter
        self._untried_actions = None
        self._untried_actions = self.untried_actions() # call untried_actions function
        return

    def untried_actions(self):
        '''
        Returns list of untried actions from a given state
        For turn 1, this is 9
        '''
        self._untried_actions = self.state.get_legal_actions() # call to get legal moves. Calls GET_LEGAL_ACTIONS (defined by user)
        return self._untried_actions

    def expand(self):
        '''
        From the present state we expand the nodes to the next possible states
        '''
        action = self._untried_actions.pop() # pops off an untried action
        next_state = self.state.move(action) # calls move function on the action to get next_state. Calls MOVE (defined by user)
        child_node = MonteCarloTreeSearchNode(
                next_state, parent=self, parent_action=action) # instantiates a new node from next state and the action selected
        self.children.append(child_node) # appends this new child node to the current node's list of children
        return child_node

    def is_terminal_node(self):
        return self.state.is_game_over() # checks is_game_over for boolean. Calls IS_GAME_OVER (defined by user)

    def is_fully_expanded(self):
        '''
        All possible actions are popped out of _untried_actions and when it is 0 we are fully expanded
        '''
        return len(self._untried_actions)==0 # returns if the untried_actions is now 0

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

    def rollout_policy(self, possible_moves):
        '''
        randomly selects a move out of possible moves and returns the random move
        '''
        return possible_moves[np.random.randint(len(possible_moves))]

    def _tree_policy(self):
        '''
        Selects node to run rollout. Is looking for the furthest terminal node to roll out.
        '''
        current_node = self

        while not current_node.is_terminal_node(): # calls a check on if this is a terminal node. Will keep looping until this is true.
            # it's checking for whether this node is already a leaf end, or if it needs to be expanded

            if not current_node.is_fully_expanded(): # check if the current node isn't fully expanded
                return current_node.expand() # if not expanded, expand current node
            else: # if current node is expanded, find best child
                current_node = current_node.best_child() # calls BEST_CHILD to get best scoring leaf

        return current_node # if current node got true from is_terminal, returns itself. otherwise returns best child.

    def rollout(self):
        '''
        On rollout call, the entire game is simulated to terminus and the outcome of the game is returned
        '''
        current_rollout_state = self.state # gets the current board state

        while not current_rollout_state.is_game_over(): # checks the state for game over boolean and loops if it's false

            possible_moves = current_rollout_state.get_legal_actions() # call to get legal moves. Calls GET_LEGAL_ACTIONS (defined by user)

            action = self.rollout_policy(possible_moves) # call random move from possible moves. Calls ROLLOUT_POLICY

            current_rollout_state = current_rollout_state.move(action) # takes action just pulled at random. Calls MOVE (defined by user)
    
        return current_rollout_state.game_result() # returns game_result when game is flagged over. Calls GAME_RESULT (defined by user)

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

    def best_action(self):
        '''
        Returns the node corresponding to the best possible move
        Carries out expansion, simulation and backpropogation
        '''
        simulation_no = 100 # how many simulations with this initial state?

        for i in range(simulation_no):

            v = self._tree_policy() # call TREE_POLICY to select the node to rollout. v is a NODE
            reward = v.rollout() # call ROLLOUT on the node v. Starts from node v and takes legal actions until the game ends. Gets the rewards
            v.backpropogate(reward) # backpropogates with the reward. Calls BACKPROPOGATE
    
        return self.best_child(c_param=0) # returns the best child node to the main function. Calls BEST_CHILD




def main(): # the first function to call to start the monte carlo search
    root = MonteCarloTreeSearchNode(state = initial_state) # instantiate the root node of the game
                                            # initial_state is to be defined by us and sent in here. how to use it? Is intended as board state
    selected_node = root.best_action() # call BEST_ACTION, get the best node for the root node to move to
    return # return what?

def get_legal_actions(self):
    '''
    Modify according to your game or
    needs. Constructs a list of all
    possible actions from current state.
    Returns a list.
    '''
    pass

def is_game_over(self):
    '''
    Modify according to your game or 
    needs. It is the game over condition
    and depends on your game. Returns
    true or false
    '''
    pass

def game_result(self):
    '''
    Modify according to your game or 
    needs. Returns 1 or 0 or -1 depending
    on your state corresponding to win,
    tie or a loss.
    '''
    pass

def move(self):
    '''
    Modify according to your game or 
    needs. Changes the state of your 
    board with a new value. For a normal
    Tic Tac Toe game, it can be a 3 by 3
    array with all the elements of array
    being 0 initially. 0 means the board 
    position is empty. If you place x in
    row 2 column 3, then it would be some 
    thing like board[2][3] = 1, where 1
    represents that x is placed. Returns 
    the new state after making a move.
    '''
    pass

class GameBoard():

    def __init__(self):
        '''
        initialize game board
        '''
        pass

    def update_board(self):
        '''
        update taken positions on the board
        '''
        pass

    def report_board(self):
        '''
        report on the current state of the game board
        '''
        pass
   