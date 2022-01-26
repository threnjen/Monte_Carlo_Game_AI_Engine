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
        self.player_count = players
        
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
        '''
        self.turn = 0 # Set the initial turn as 0
        
        current_player=self.game.get_legal_actions()[1] # Get starting player

        self.montecarlo = MonteCarloEngine(current_player) # initiate the monte carlo engine
        self.current_node = self.montecarlo.root

        while not self.game.is_game_over():

            self.turn += 1 # increments the game turn

            # Establish number of simulations per turn. Uncomment other choices below for reduced sims per turn.
            self.sims_this_turn = simulations
            #self.sims_this_turn = int(np.ceil(self.sims_this_turn*.8)) # get the number of simulations for the rounds
            #self.sims_this_turn = int(np.ceil(self.simulations/(self.turn))) # get the number of simulations for the rounds
            
            # Beginning of game repoprting:
            print("\n\nTurn "+str(self.turn))
            print('Current board state: ')
            print(self.game._state) # prints the game board            
            print("Game gets "+str(self.sims_this_turn)+' simulations for this turn.'+' (play_game_byturns)')
            print("Player's turn: Player "+str(current_player)+' (play_game_byturns)') #whose turn is it?

            # Run the monte carlo engine for this turn. This accesses the meat of the engine right here!
            # returns a chosen action to implement
            print(current_player)
            self.action, self.current_node = self.montecarlo.play_turn(self.sims_this_turn, self.game, current_player, self.current_node)
            
            self.state = self.game.update_game(self.action, current_player) # updates the true game state with the MC simmed action

            current_player = self.game.get_legal_actions()[1] # update current player

        # Game over report
        print("\n\n\nGame over. Game took "+str(self.turn)+" turns."+' (play_game_byturns)')
        self.scores = self.game.game_result() # get game scores
        print(self.game._state) # print final board
        print(self.scores) # print final scores

    #def play_entire_game(self, simulations, game_label):
        #'''
        #Initializes gameplay
        #Will run entire game start to finish on a single MC
        #'''

        #self.simulations = simulations
        #self.turn = 0

        #self.actions=self.game.get_legal_actions()
        #self.legal_actions = self.actions[0]
        #self.player = self.actions[1]  

        #self.turn_engine = MonteCarloEngine()

        #first_action_list=[]

        #for i in range(self.simulations):

        #    self.action = self.turn_engine.play_turn(1, self.game, self.player) 
        #    first_action_list.append(tuple(self.action))         
        
        #df = pd.DataFrame(first_action_list)
        #df['pairs'] = df.apply(lambda x: (str(x[0])+", "+str(x[1])), axis=1)
        #df.to_pickle('first_action_list'+str(game_label)+'.pkl')

class MonteCarloEngine():

    def __init__(self, current_player): #, legal_actions=None, player=None
        '''
        Instantiates root monte carlo node
        '''    
        self.root = MonteCarloNode(player=current_player)

    def play_turn(self, num_sims, game, current_player, current_node):
        '''
        Received a specific game state from which to make a move

        Runs a given number of simulations to terminus, according to the Monte Carlo schema:
        1. Find next node to _rollout (Expansion)
        2. _rollout game (Simulation)
        3. _backpropogate

        Returns the optimal turn action for the game state it was provided
        '''
        for i in range(num_sims):  # Run x simulations for this turn
            # COPY THE GAME STATE HERE AND ROLL OUT ON IT NOT THE REAL GAME
            self.game_copy = copy.deepcopy(game)

            while not self.game_copy.is_game_over(): # for as long as the copied game is not over:

                self.rollout_node = self._selection(current_node, current_player) # call _selection to move to a node to roll out, taking the moves along the way
                self.rollout_node.player_owner

                self.scores = self._rollout() # call _rollout to finish simulating the game

                self._backpropogate(self.scores, self.rollout_node) # _backpropogates with the reward starting from the rollout_node

        # Simulations have finished running, time to get the best move and return it to the game engine
        self.selected_node = self.root.best_child(print_weights=False) # Calls BEST_CHILD for the node we started on
        self.best_action = self.selected_node.node_action

        return self.best_action, self.selected_node # returns the best child node to the main function.

    def _selection(self, node, current_player):
        '''
        Selects node to run _rollout. Is looking for the furthest terminal node to roll out.

        While current node is NOT a leaf: Evaluate by if it has children or not. Children = not leaf. No children = leaf.
            return current child node with highest score (best_child)
            Take the action of that node
                
        Now we are on a leaf.

        Now follow _expansion protocol.
        '''
        self.current_node = node
        self.player=current_player # call legal moves to get the current player

        def move_node(current_node, player):
            action = current_node.node_action # get the action to take from the current node
            self.state = self.game_copy.update_game(action, player) # update the game copy with the action and the player taking the move

        # Evaluate our incoming node.
            # Does it have children?
            # has it been visited?
            # Who is the player for the node?

        # Are we at a leaf node?

        while len(self.current_node.children) != 0 and not self.current_node.number_of_visits == 0: 
            # HAS CHILDREN
            # HAS BEEN VISITED
            self.current_node = self.current_node.best_child(print_weights=False) # change the current node to the best child
            move_node(self.current_node, self.player) # take the move of the new current node
            self.player=self.game_copy.get_legal_actions()[1]
            # loop and check again if we hit a leaf
            # this branch may move more than one node down to find a new expansion point
        
        # Now we have reached a leaf node which has never been visited
        if self.current_node.number_of_visits == 0 and not self.current_node == self.root:
            # NO CHILDREN
            # NOT VISITED
            # NOT ROOT 
            self._expansion(self.current_node, self.player) # expand the current leaf
            return self.current_node # return current node for rollout

        elif self.current_node.number_of_visits == 0 and self.current_node == self.root:
            # NO CHILDREN
            # NOT VISITED
            # IS ROOT
            self._expansion(self.current_node, self.player) # expand the root
            self.current_node = self.current_node.best_child(print_weights=False) # get the best child of the root
            move_node(self.current_node, self.player) # move to the best child
            return self.current_node # return the best child as current node for rollout
        
        else:
            # NO CHILDREN
            # IS VISITED
            # means game is over
            return self.current_node


    def _expansion(self, current_node, current_player):
        '''
        From the present state we _expansion the nodes to the next possible states
        We take in a node with no children and we will _expansion it to all children

        For each available action for the current node, add a new state to the tree

        Query the game state for all of the legal actions, and store that in a list
        As we pop items off the list and apply them to the
        '''

        actions_to_pop=self.game_copy.get_legal_actions()[0] # call to get legal moves. Calls GET_LEGAL_ACTIONS in GameLogic

        while len(actions_to_pop) != 0:

            # pops off node actions randomly so that the order of try-stuff isn't as deterministic
            action = actions_to_pop[np.random.randint(len(actions_to_pop))]
            actions_to_pop.remove(action) # pops off an untried action
            #action = actions_to_pop.pop() # uncomment this to pop actions off the end of the list instead
            
            node_depth = current_node.depth # get the depth of the current node, for labeling
            node_label = ('Action '+str(action)) # create the node label

            # make the child node for the popped action:
            # parent: current node incoming to the expansion function
            # node_action: the action just popped off the list
            # label: just made, is used to print node info in the GUI
            # depth: depth of the new node. Is current node's depth +1
            # player: the current player who owns this new action
            child_node = MonteCarloNode(parent=current_node, node_action=action, label=node_label, depth = (node_depth+1), player=current_player) 

            current_node.children.append(child_node) # appends this new child node to the current node's list of children            


    def _rollout(self):
        '''
        On _rollout call, the entire game is simulated to terminus and the outcome of the game is returned
        ''' 

        while not self.game_copy.is_game_over():  # checks the state for game over boolean and loops if it's false

            actions=self.game_copy.get_legal_actions()# call to get legal moves. Calls GET_LEGAL_ACTIONS in GameLogic object
            legal_actions = actions[0]
            player = actions[1]

            #if player != current_player:
            #    #print("Not active player")
            #    killer_action = self.game_copy.check_killer_move(player)
            #    if killer_action:
            #        action = killer_action
            #        #print("kill action")
            #    else:
            #        action = legal_actions[np.random.randint(len(legal_actions))]

            action = legal_actions[np.random.randint(len(legal_actions))]
            
            #print("Player "+str(player)+' chose '+str(action))
            self.game_copy.update_game(action, player) # takes action just pulled at random. Calls MOVE in GameLogic object
        
        #print("Game is over")
        self.scores = self.game_copy.game_result()
        #print(self.game_copy._state)
        #print(self.scores)
        return self.scores


    def _backpropogate(self, scores, node):
        '''
        all node statistics are updated. Until the parent node is reached.
        All visits +1
        win stats/scores/etc are incrememnted as needed
        '''
        
        owner = node.player_owner
        node.number_of_visits += 1  # updates self with number of visits
        # updates self with reward (sent in from _backpropogate)
        node.total_score += scores[owner]
        #print("Current: Depth "+str(node.depth)+' '+str(node.label)+" Total: "+str(node.total_score)+" Visits: "+str(node.number_of_visits))

        if node.parent:  # if this node has a parent,
            # call _backpropogate on the parent, so this will continue until root note which has no parent
            self._backpropogate(scores, node.parent)


class MonteCarloNode():

    # node_action=None, state=None,
    def __init__(self, parent=None, node_action=None, label='Root Node', depth=0, player=None): #, legal_actions=None
        self.parent = parent # the node that spawned this node. Root is None.
        self.node_action = node_action # the action being taken at this node
        self.children = [] # the storage for the children of this node
        self.number_of_visits = 0  # number of times current node is visited
        self.total_score = 0 # total score for this node ONLY for its owner
        self.label = label # label for the node, is used in GUI reporting
        self.depth = depth # depth of the node
        self.player_owner = player # the player who owns/plays this node layer. Should be same player at any given depth.

        #print(self.player_owner)

        return

    def best_child(self, c_param=np.sqrt(2), print_weights=False):
        '''
        selects best child node from available array
        first param is exploitation and second is exploration
        '''

        # makes an array of the leaf calculations
        choices_weights = []
        for c in self.children:
            try:
                score = (c.total_score / c.number_of_visits) + c_param * (np.sqrt(np.log(self.number_of_visits) / c.number_of_visits))
                choices_weights.append(score)
            except:
                score=1000
                choices_weights.append(1000)
            
            if print_weights==True:
                print(c.depth, c.label, score)

        return self.children[np.argmax(choices_weights)] # gets index of max score and sends back identity of child

class Player():
    def __init__(self):
        self.score = 0

players = 2
game = GameEngine(players)
game.play_game_byturns(simulations = 1000)
#game.play_entire_game(simulations = 1000, game_label='array_1000')
