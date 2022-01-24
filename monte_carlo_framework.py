# this file is the custom monte carlo framework for our AI to plug into

import numpy as np
import copy
import pandas as pd
#from simple_array_game import SimpleArrayGame as Game
from tic_tac_toe import Game
from random import randint


class GameEngine():
    
    def __init__(self, players):
        '''
        Instantiates the game logic and the root monte carlo node
        '''
        self.game = Game()
        self.state = self.game._state
        self.players = {}
        
        for i in range(players):
            self.players[i] = TurnEngine()

        
    def get_legal_actions(self):
        '''
        Hook #1
        report on currently available actions after checking board space
        returns list of actions

        '''
        return self.game.get_legal_actions()

    def update_game(self, action, player):
        '''
        Hook #2
        Send action to game and get updated game state
        returns game._state

        Also needs to pass player id !

        Need a way to designate when the player's turn is over

        '''
        return self.game.update_game(action, player)

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

    def play_game_byturns(self, simulations):
        '''
        Intializes gameplay
        Will play game until game over condition is met
        Each turn will run a MC for that turn choice
        '''

        self.simulations = simulations # set number of simulations to run
        self.turn = 0 # set the turns number for start of game (0 for game start)
        self.last_action = None

        for i in self.players:
            self.players[i].current_node = self.players[i].root # set the current node for each player as the root
        
        while not self.game.is_game_over():
            
            self.current_player=self.game.get_legal_actions()[1] # get current player
            print("Player's turn: Player "+str(self.current_player)+' (play_game_byturns)') #whose turn is it?

            print("Turn "+str(self.turn)+". Current board state:"+' (play_game_byturns)')
            print(self.game._state) # prints the game board

            self.turn += 1 # increments the game turn

            self.sims_this_turn = int(np.ceil(self.simulations/(self.turn))) # get the number of simulations for the rounds
            print("Game gets "+str(self.sims_this_turn)+' simulations for this turn.'+' (play_game_byturns)')

            self.current_node = self.players[self.current_player].current_node # get current node
            print("Player's starting node: "+str(self.current_node.label)+' (play_game_byturns)')

            self.actions=self.game.get_legal_actions() # poll for legal actions
            self.legal_actions = self.actions[0] # get legal actions list
            print("Legal actions this round are: "+str(self.legal_actions)+' (play_game_byturns)')

            self.action, self.players[self.current_player].current_node = self.players[self.current_player].play_turn(self.sims_this_turn, self.game, self.current_player, self.current_node, self.last_action)
            print("New node is: "+str(self.players[self.current_player].current_node.label)+' (play_game_byturns)'+'\n\n')
    
            self.state = self.game.update_game(self.action, self.current_player) # updates the true game state with the action
            self.last_action = self.action

        print("Game over. Game took "+str(self.turn)+" turns."+' (play_game_byturns)')
        self.scores = self.game.game_result() # get game scores
        print(self.game._state) # print final board
        print(self.scores) # print final scores

    def play_entire_game(self, simulations, game_label):
        '''
        Initializes gameplay
        Will run entire game start to finish on a single MC
        '''

        self.simulations = simulations
        self.turn = 0

        self.actions=self.game.get_legal_actions()
        self.legal_actions = self.actions[0]
        self.player = self.actions[1]  

        self.turn_engine = TurnEngine(self.legal_actions, self.player)

        first_action_list=[]

        for i in range(self.simulations):

            self.action = self.turn_engine.play_turn(1, self.game, self.player) 
            first_action_list.append(tuple(self.action))         
        
        df = pd.DataFrame(first_action_list)
        df['pairs'] = df.apply(lambda x: (str(x[0])+", "+str(x[1])), axis=1)
        df.to_pickle('first_action_list'+str(game_label)+'.pkl')

class TurnEngine():

    def __init__(self): #, legal_actions=None, player=None
        '''
        Instantiates root monte carlo node
        '''    
        self.root = MonteCarloNode() # legal_actions=legal_actions, node_action=None, state=self.game._state,
        #self.player = player


    def play_turn(self, num_sims, game, current_player, node, last_action):
        '''
        Received a specific game state from which to make a move

        Runs a given number of simulations to terminus, according to the Monte Carlo schema:
        1. Find next node to _rollout (Expansion)
        2. _rollout game (Simulation)
        3. _backpropogate

        Returns the optimal turn action for the game state it was provided
        '''
        #print("Starting turn calculation with "+str(num_sims)+" sims")

        self.node = node
        self.last_action = last_action

        print("Starting sim on: "+str(self.node.label)+' player '+str(current_player)+' (play_turn)')

        for i in range(num_sims):  # how many simulations with this initial state?

            # COPY THE GAME STATE HERE AND ROLL OUT ON IT NOT THE REAL GAME
            self.game_copy = copy.deepcopy(game)

            while not self.game_copy.is_game_over():

                self.rollout_node = self._selection(self.node, self.last_action) # call _selection to move to node to roll out, taking the moves along the way

                # call _rollout on the node
                self.reward = self._rollout(current_player)

                self._backpropogate(self.reward, self.rollout_node) # _backpropogates with the reward starting from the rollout_node

                self.scores = self.game_copy.game_result()

        print("Current self.node after simulation: "+str(self.node.label)+' (play_turn)')
        print(self.node.children)
        self.selected_node = self.node.best_child() # returns the best child node to the main function. Calls BEST_CHILD
        print("Selected best child node: "+str(self.selected_node)+' (play_turn)')
        self.best_action = self.selected_node.node_action

        #print("Best turn move is: "+str(self.best_action))

        return self.best_action, self.selected_node

    def _selection(self, node, last_action):
        '''
        Selects node to run _rollout. Is looking for the furthest terminal node to roll out.
        This function needs some work on the logic to make it work properly

        While current node is NOT a leaf: Evaluate by if it has children or not. Children = not leaf. No children = leaf.
            return current child node with highest score (best_child)
            Take the action of that node
                
        Now we are on a leaf.

        Now follow _expansion protocol.
        '''
        self.current_node = node

        print("Entering _SELECTION function")
        print("Our node to check on entry is: "+str(node.label))

        def move_node(current_node):
            self.current_node = current_node
            self.player=self.game_copy.get_legal_actions()[1] # call legal moves to get the current player
            self.action = self.current_node.node_action # get the action to take from the current node
            self.state = self.game_copy.update_game(self.action, self.player) # update the game copy with the action and the player taking the move

        ### POINT OF FIX HERE. Only make new leaves as we need to explore them, creating one at a time. Otherwise calling BEST_CHILD breaks if there
        # are not enough sims to expand the leaf.
        while len(self.current_node.children) != 0: # while the current node has any child nodes (meaning node is not a leaf):
            print("Current node children: "+str(self.current_node.children))# remove the child node for the last action taken in the game
            self.current_node = self.current_node.best_child() # change the current node to the best child
            move_node(self.current_node) # take the move of the new current node
            # this loop repeats until the current node has no child nodes aka we have reached a leaf node
        
        # we have reached a leaf node
        if self.current_node.number_of_visits == .001 and not self.current_node == self.root: # if this leaf has never been visited, this will be our current node
            print(self.current_node.number_of_visits)
            print("This node has not been visited")
            return self.current_node
        else:
            try:
                print("Expand leaf: Go into expansion function")
                self._expansion(self.current_node) # _expansion the current leaf
                print("Get best leaf: Call best child on current node")
                self.current_node = self.current_node.best_child() # get the best child of the current leaf
                move_node(self.current_node)
            except: 
                pass
            # take action on the node before returning
            return self.current_node # return the child


    def _expansion(self, current_node):
        '''
        From the present state we _expansion the nodes to the next possible states
        We take in a node with no children and we will _expansion it to all children

        For each available action for the current node, add a new state to the tree

        Query the game state for all of the legal actions, and store that in a list
        As we pop items off the list and apply them to the
        '''

        print("Entering EXPANSION function")
        self.current_node = current_node

        self.actions=self.game_copy.get_legal_actions()# call to get legal moves. Calls GET_LEGAL_ACTIONS in GameLogic object
        self.actions_to_pop = self.actions[0]
        self.player = self.actions[1] #identify current legal player

        #print("Popping actions off of: "+str(self.current_node.label))

        while len(self.actions_to_pop) != 0:

            # pops off node actions randomly so that the order of try-stuff isn't as deterministic
            self.action = self.actions_to_pop[np.random.randint(len(self.actions_to_pop))]
            self.actions_to_pop.remove(self.action) # pops off an untried action

            node_depth = self.current_node.depth
            node_label = ("Action "+str(self.action))

            child_node = MonteCarloNode(parent=self.current_node, node_action=self.action, label=node_label, depth = (node_depth+1)) #   # instantiates a new node from next state and the action selected
            current_node.children.append(child_node) # appends this new child node to the current node's list of children            


    def _rollout(self, current_player):
        '''
        On _rollout call, the entire game is simulated to terminus and the outcome of the game is returned
        '''

        print("Entering ROLLOUT function")
        self.current_player = current_player

        while not self.game_copy.is_game_over():  # checks the state for game over boolean and loops if it's false

            self.actions=self.game_copy.get_legal_actions()# call to get legal moves. Calls GET_LEGAL_ACTIONS in GameLogic object
            self.legal_actions = self.actions[0]
            self.player = self.actions[1]

            #action = self._rollout_policy(possible_moves) # Calls _rollout_POLICY in case needs more complicated
            self.action = self.legal_actions[np.random.randint(len(self.legal_actions))] # call random move from possible moves
            self.game_copy.update_game(self.action, self.player) # takes action just pulled at random. Calls MOVE in GameLogic object

        # returns game_result when game is flagged over. Calls GAME_RESULT in GameLogic object
        self.scores = self.game_copy.game_result()
        return self.scores[self.current_player]


    def _backpropogate(self, reward, node):
        '''
        all node statistics are updated. Until the parent node is reached.
        All visits +1
        win stats/scores/etc are incrememnted as needed
        '''
        print("Entering BACKPROPOGATE function")

        node.number_of_visits += 1  # updates self with number of visits
        # updates self with reward (sent in from _backpropogate)
        node.total_score += reward

        print(node.label, node.number_of_visits)

        if node.parent:  # if this node has a parent,
            # call _backpropogate on the parent, so this will continue until root note which has no parent
            self._backpropogate(reward, node.parent)


class MonteCarloNode():

    # node_action=None, state=None,
    def __init__(self, parent=None, node_action=None, label='Root Node', depth=0): #, legal_actions=None
        # self.state = state # board state, in tic tac toe is 3x3 array. (defined by user)
        # none for the root node and for other nodes is = node derived from. First turn will be none
        self.parent = parent
        self.node_action = node_action # none for root but is = parent action for other nodes
        #self.action_label = action_label
        self.children = []  # all possible actions from current node
        self.number_of_visits = .001  # number of times current node is visited
        self.total_score = 0
        self.label = label
        self.depth = depth
        #self._untried_actions = None
        # call to get legal moves. Calls GET_LEGAL_ACTIONS in GameLogic object
        #self._untried_actions = legal_actions
        return

    def best_child(self, c_param=2):
        '''
        selects best child node from available array
        first param is exploitation and second is exploration
        '''
        print("Entering BEST_CHILD function")
        # makes an array of the leaf calculations
        choices_weights = []
        for c in self.children:         
            score = (c.total_score / c.number_of_visits) + c_param * (np.sqrt(abs(np.log(self.number_of_visits)) / c.number_of_visits))
            choices_weights.append(score)
            #print(c.label, score)

        return self.children[np.argmax(choices_weights)] # gets index of max score and sends back identity of child

class Player():
    def __init__(self):
        self.score = 0

players = 2
game = GameEngine(players)
game.play_game_byturns(simulations = 100)
#game.play_entire_game(simulations = 1000, game_label='array_1000')
