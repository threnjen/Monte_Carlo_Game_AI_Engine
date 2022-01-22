# this file is the custom monte carlo framework for our AI to plug into


import numpy as np
import copy
from collections import defaultdict

class GameEngine():
    
    def __init__(self):
        '''
        Instantiates the game logic and the root monte carlo node
        '''    
        self.game = SimpleArrayGame()
        self.state = self.game._state

    def update_game(self, action):
        '''
        Hook #1
        Send action to game and get updated game state
        returns game._state
        '''
        return self.game.update_game(action)

    def get_legal_actions(self):
        '''
        Hook #2
        report on currently available actions after checking board space
        returns list of actions
        '''
        return self.game.get_legal_actions()

    def is_game_over(self):
        '''
        Hook #3
        Returns true or false
        '''
        return self.game.is_game_over()

    def game_result(self):
        '''
        Hook #4
        Returns endgame score
        '''
        return self.game.game_result()  

    def play_game(self):

        '''
        Intializes gameplay
        Will play game until game over condition is met
        Each turn will run a MC for that turn choice
        '''
        
        while not self.game.is_game_over():
            
            print("New Turn. Current board state:")
            print(self.state)

            legal_actions=self.game.get_legal_actions()

            self.current_turn = TurnEngine(legal_actions)
            self.action = self.current_turn.play_turn(10000, self.game) # sends number of simulations and current game to turn engine
                                                                    # gets back the optimal action

            print("filling: "+str(self.action))

            self.state = self.game.update_game(self.action) # updates the true game state with the action

            # opponent takes turn. commented out because we don't need that right now.
            #possible_moves = self.game.get_legal_actions()
            #action = possible_moves[np.random.randint(len(possible_moves))]
            #self.state = self.game.update_game(action)
        
        self.end_score = self.game.game_result()
        print(self.game._state)
        print(self.end_score)


class TurnEngine():
    
    def __init__(self, legal_actions=None):
        '''
        Instantiates root monte carlo node
        '''    
        self.root = MonteCarlo(legal_actions=legal_actions) # parent_action=None, state=self.game._state,

    def play_turn(self, num_sims, game):
        '''
        Received a specific game state from which to make a move

        Runs a given number of simulations to terminus, according to the Monte Carlo schema:
        1. Find next node to rollout (Expansion)
        2. Rollout game (Simulation)
        3. Backpropogate

        Returns the optimal turn choice for the game state it was provided
        '''
        print("Starting turn calculation with "+str(num_sims)+" sims")

        for i in range(num_sims): # how many simulations with this initial state?

            # COPY THE GAME STATE HERE AND ROLL OUT ON IT NOT THE REAL GAME
            self.game_copy = copy.deepcopy(game)

            v = self._tree_policy(self.root) # call TREE_POLICY to select the node to rollout. v is a NODE
            #print("Rollout node: "+str(v))

            reward = self.rollout() # call ROLLOUT on the node v. Starts from node v and takes legal actions until the game ends. Gets the rewards
            #print("Reward: "+str(reward))

            #print(v)
            self.backpropogate(reward, v) # backpropogates with the reward. Calls BACKPROPOGATE
    
        selected_node = self.root.best_child(c_param=2) # returns the best child node to the main function. Calls BEST_CHILD
        best_action = selected_node.action_label
        print("Best move is: "+str(best_action))

        return best_action

    def _tree_policy(self, node):
        '''
        Selects node to run rollout. Is looking for the furthest terminal node to roll out.
        This function needs some work on the logic to make it work properly
        '''
        current_node = node

        #print("Entering Tree Policy function")
        while len(current_node.children)==0:

            #print("Expansion is still possible")

            while len(current_node._untried_actions)!=0: # check if the current node isn't fully expanded
                #print("Current node is not fully expanded, expanding node")
                self.expand(current_node) # if not expanded, expand current node
        
        # logic here is only expanding one node no matter what, i think
        # if current node is expanded, find best child
        #print("Current node is fully expanded, getting best child")
        current_node = current_node.best_child() # calls BEST_CHILD to get best scoring leaf
                
        return current_node
    
    def expand(self, current_node):
        '''
        From the present state we expand the nodes to the next possible states
        '''
        #print("Expanding nodes")
        action = current_node._untried_actions.pop() # pops off an untried action
        #next_state = self.game_copy.update_game(action) # calls move function on the action to get next_state. Calls MOVE in GameLogic object
        child_node = MonteCarlo(parent=current_node, action_label=action) # parent_action=action, state=next_state,  # instantiates a new node from next state and the action selected
        current_node.children.append(child_node) # appends this new child node to the current node's list of children
        #return child_node

    def rollout(self):
        '''
        On rollout call, the entire game is simulated to terminus and the outcome of the game is returned
        '''
        #print("Now entering rollout function")
        while not self.game_copy.is_game_over(): # checks the state for game over boolean and loops if it's false
            #print("Game is not over")

            #print("Getting possible moves")
            possible_moves = self.game_copy.get_legal_actions() # call to get legal moves. Calls GET_LEGAL_ACTIONS in GameLogic object
            #print(possible_moves)

            #action = self.rollout_policy(possible_moves) # Calls ROLLOUT_POLICY in case needs more complicated
            action = possible_moves[np.random.randint(len(possible_moves))] # call random move from possible moves
            #print("Picked random action: "+str(action))

            self.game_copy.update_game(action) # takes action just pulled at random. Calls MOVE in GameLogic object
            #print("Updating game with move")

        #print("This simulation has ended; returning result")
        return self.game_copy.game_result() # returns game_result when game is flagged over. Calls GAME_RESULT in GameLogic object

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
            self.backpropogate(reward, node.parent) # call backpropogate on the parent, so this will continue until root note which has no parent


class MonteCarlo():

    def __init__(self, parent=None, action_label = None, legal_actions=None): #parent_action=None, state=None, 
        #self.state = state # board state, in tic tac toe is 3x3 array. (defined by user)
        self.parent = parent # none for the root node and for other nodes is = node derived from. First turn will be none
        #self.parent_action = parent_action # none for root but is = parent action for other nodes
        self.action_label = action_label
        self.children = [] # all possible actions from current node
        self.number_of_visits = 0 # number of times current node is visited
        self.results = defaultdict(int) 
        self.results[1] = 0 # in this tic tac toe example, this is the win counter
        self.results[-1] = 0 # in this tic tac toe example, this is the loss counter
        self._untried_actions = None
        self._untried_actions = legal_actions # call to get legal moves. Calls GET_LEGAL_ACTIONS in GameLogic object
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
        choices_weights = []
        for c in self.children:
            try:
                score = (c.node_score() / c.node_visits()) + c_param * np.sqrt((np.log(self.node_visits())) / c.node_visits())
                choices_weights.append(score)
            except:
                choices_weights.append(1000)

        #choices_weights = [(c.node_score() / c.node_visits()) + c_param * np.sqrt((np.log(self.node_visits())) / c.node_visits()) for c in self.children] 
                        #calculates scores for child nodes
        return self.children[np.argmax(choices_weights)] # gets index of max score and sends back identity of child

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


game = GameEngine()
game.play_game()