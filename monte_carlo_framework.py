# this file is the custom monte carlo framework for our AI to plug into

import numpy as np
import copy
import sys
import pandas as pd
#from simple_array_game import SimpleArrayGame as Game
#from tic_tac_toe import Game
from otrio import Game
#from connect_four import Game
from random import randint


class GameEngine():
    
    def __init__(self, players):
        """
        Initializes game
        Sets player count
        """        
        self.game = Game(players)
        #self.state = self.game._state
        self.player_count = players

        self.game_log = pd.DataFrame(columns=['Turn', 'Actions', 'Player', 'Action', 'Score', 'Simulations'])
        
    def get_legal_actions(self):
        """
        Hook #1
        Get currently available actions and active player to take an action from the list

        Requires a list with two indices:
        0: list of legal actions
        1: active player ID

        Format [[list of legal actions], active player ID]

        The Monte Carlo does not care about the contents of the list of legal actions, and will return
        a list item in exactly the same format it presents in the list

        The game logic must manage the correct player turns. The Monte Carlo engine will assign the
        next legal action to the player passed, with no safety checks.

        Returns:
            [list]: List of: list of legal actions and active player ID
        """        

        return self.game.get_legal_actions()

    def update_game(self, action, player):
        """
        Hook #2
        Send action choice and player to game

        After selecting an item from the list of legal actions (see Hook #1),
        Sends the item back to the game logic. Item is sent back in exactly
        the same format as received in the list of legal actions.

        Also returns active player ID for action

        Args:
            action (list item): selected item from list of legal actions
            player (int): player number
        """        
        return self.game.update_game(action, player)

    def is_game_over(self):
        """
        Hook #3
        Checks if game has ended

        Requires only True or False

        Returns:
            [True/False]: True/False if game is over
        """        
        return self.game.is_game_over()

    def game_result(self):
        """
        Hook #4
        Retrieves game score

        Must be a dictionary in format {playerID: Score}
        Where playerID matches IDs sent with get_legal_actions

        Returns:
            [dict]: dictionary in format playerID: score
        """        
        return self.game.game_result()

    def play_game_byturns(self, simulations):
        """
        Intializes Monte Carlo engine
        Will play a single game until game over condition is met

        Args:
            simulations (int): Number of simulations to run per turn
        """        

        self.turn = 0 # Set the initial turn as 0
        
        current_player=self.game.get_legal_actions()[1] # Get starting player

        self.montecarlo = MonteCarloEngine(current_player) # initiate the monte carlo engine
        self.current_node = self.montecarlo.root # set first node as monte carlo root

        self.sims_this_turn = simulations # set number of simulations

        while not self.game.is_game_over():

            #turn_log = pd.DataFrame(columns=['Turn', 'Actions', 'Player', 'Action', 'Score', 'Simulations'])
            turn_log = {}

            self.turn += 1 # increments the game turn
            turn_log['Turn']=self.turn

            actions=self.game.get_legal_actions()[0]
            turn_log['Actions']=actions

            # Add simulation decay if desired. Uncomment choices below for two types of simulation decay.
            self.sims_this_turn = int(np.ceil(self.sims_this_turn*.9)) # simulation decay of .9 each round
            #self.sims_this_turn = int(np.ceil(self.simulations/(self.turn))) # simulation decay to absolute simulations/turn each round
            
            # Beginning of game repoprting:
            print("\n\nTurn "+str(self.turn))
            print('Current board state: ')
            print(self.game._state) # prints the game board            
            print("Game gets "+str(self.sims_this_turn)+' simulations for this turn.')
            print("Player's turn: Player "+str(current_player)) #whose turn is it?

            # Run the monte carlo engine for this turn. This accesses the meat of the engine right here!
            # returns a chosen action to implement and the new active node
            self.current_node = self.montecarlo.play_turn(self.sims_this_turn, self.game, current_player, self.current_node)
            best_action = self.current_node.node_action # gets action of the returned node

            self.game.update_game(best_action, current_player) # updates the true game state with the MC simmed action
            turn_log['Simulations'] = self.sims_this_turn
            turn_log['Player']= current_player
            turn_log['Action']= str(best_action)
            self.scores = self.game.game_result() # get game scores
            turn_log['Score']=self.scores[current_player]

            current_player = self.game.get_legal_actions()[1] # update current player

            self.game_log = self.game_log.append(turn_log, ignore_index=True)

        # Game over report
        print("\n\n\nGame over. Game took "+str(self.turn)+" turns.")
        self.scores = self.game.game_result() # get game scores
        print(self.game._state) # print final board
        print(self.scores) # print final scores

        self.game_log.to_pickle('logs/'+self.game.name+'_game_log_'+str(randint(1,1000000))+'.pkl')
        #first_action_list=[]

        #for i in range(self.simulations):

        #    self.action = self.turn_engine.play_turn(1, self.game, self.player) 
        #    first_action_list.append(tuple(self.action))         
        
        #df = pd.DataFrame(first_action_list)
        #df['pairs'] = df.apply(lambda x: (str(x[0])+", "+str(x[1])), axis=1)
        #df.to_pickle('first_action_list'+str(game_label)+'.pkl')

class MonteCarloEngine():

    def __init__(self, current_player): #, legal_actions=None, player=None
        """
        Instantiates root monte carlo node
        Assigns starting player to root node

        Args:
            current_player (int): Current player id
        """          
        self.root = MonteCarloNode(player=current_player)

    def play_turn(self, num_sims, game, current_player, current_node):
        """
        Receives a specific game state from which to make a move

        Runs a given number of simulations, according to the Monte Carlo schema:
        1. Find next node to rollout (_selection)
        2. Expands nods as needed (_expansion, from _selection)
        3. Simulate game to terminus (_rollout)
        4. Back-update scores starting with rollout node (_backpropogate)

        Returns the chosen turn action for the game state it was provided

        Args:
            num_sims (int): number of simulations to run for turn
            game (object instance): game logic object instance
            current_player (int): current player ID
            current_node (object instance): current MonteCarloNode object instance

        Returns:
            selected_node (object instance): MonteCarloNode object instance
        """        
        self.current_node = current_node # set current node to received node

        for i in range(num_sims):  # Run x simulations for this turn
            
            # COPY THE GAME STATE HERE AND ROLL OUT ON IT NOT THE REAL GAME
            self.game_copy = copy.deepcopy(game)

            while not self.game_copy.is_game_over(): # for as long as the copied game is not over:

                self.rollout_node = self._selection(self.current_node, current_player) # call _selection to find the node to roll out, taking the moves along the way

                self.scores = self._rollout() # call _rollout to finish simulating the game

                self._backpropogate(self.scores, self.rollout_node) # _backpropogates with the scores starting from the rollout_node

        # Simulations have finished running, time to get the best move and return it to the game engine
        selected_node = self.current_node.best_child(print_weights=False) # Calls BEST_CHILD for the node we started on

        return selected_node # returns the best child node to the main function.

    def _selection(self, node, current_player):
        """
        Selects node to run simulation. Is looking for the furthest terminal node to roll out.

        Evaluate incoming node. Is node a leaf?
            If no: move to best scoring child. Repeat until yes.
            If yes: arrive at leaf
        
        After arriving at a leaf. Has leaf been visited?
            If no: expand leaf to all possible actions, move to first action, and return child as rollout node
            If yes: return leaf as rollout node

        Args:
            node [object instance]: MonteCarloNode object instance
            current_player (int): current player ID

        Returns:
            current_node (object instance): MonteCarloNode object instance
        """        

        current_node = node
        self.player=current_player # call legal moves to get the current player

        def move_node(current_node, player):
            action = current_node.node_action # get the action to take from the current node
            #self.state = 
            self.game_copy.update_game(action, player) # update the game copy with the action and the player taking the move

        # Evaluate our incoming node.
        while len(current_node.children) > 0 and current_node.number_of_visits > 0: 
            # HAS CHILDREN
            # HAS BEEN VISITED
            current_node = current_node.best_child(print_weights=False) # change the current node to the best child
            move_node(current_node, self.player) # take the move of the new current node
            self.player=self.game_copy.get_legal_actions()[1]
            # loop and check again if we hit a leaf; this branch may move more than one node down to find a new expansion point

        # Now we have reached a leaf node

        if len(self.game_copy.get_legal_actions()[0])==0:
            # NO CHILDREN
            # HAS BEEN VISITED
            # means game is over
            return current_node

        elif current_node.number_of_visits == 0 and not current_node == self.root:
            # NO CHILDREN
            # NOT VISITED
            # NOT ROOT 
            self._expansion(current_node, self.player) # expand the current leaf
            return current_node # return current node for rollout

        elif len(current_node.children) == 0 and current_node.number_of_visits > 0 and not current_node == self.root:
            # NO CHILDREN
            # IS VISITED
            # NOT ROOT
            self._expansion(current_node, self.player) # expand the root
            current_node = current_node.best_child(print_weights=False) # get the best child of the root
            move_node(current_node, self.player) # move to the best child
            return current_node # return the best child as current node for rollout

        elif current_node.number_of_visits == 0 and current_node == self.root:
            # NO CHILDREN
            # NOT VISITED
            # IS ROOT
            self._expansion(current_node, self.player) # expand the root
            current_node = current_node.best_child(print_weights=False) # get the best child of the root
            move_node(current_node, self.player) # move to the best child
            return current_node # return the best child as current node for rollout


    def _expansion(self, current_node, current_player):
        """
        From the present state we _expansion the nodes to the next possible states
        We take in a node with no children and we will _expansion it to all children

        For each available action for the current node, add a new state to the tree

        Query the game state for all of the legal actions, and store that in a list
        As we pop items off the list and apply them to the

        Args:
            current_node (object instance): MonteCarloNode object instance
            current_player (int): current player ID
        """        
        actions_to_pop=self.game_copy.get_legal_actions()[0] # call to get legal moves. Calls GET_LEGAL_ACTIONS in GameLogic

        while len(actions_to_pop) != 0:

            # pops off node actions randomly so that the order of try-stuff isn't as deterministic
            action = actions_to_pop[np.random.randint(len(actions_to_pop))]
            actions_to_pop.remove(action) # pops off an untried action
            #action = actions_to_pop.pop() # uncomment this to pop actions off the end of the list instead in deterministic order
            
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
        """
        On _rollout call, the entire game is simulated to terminus and the outcome of the game is returned

        Returns:
            scores (dict): dictionary of scores with player ID as keys
        """        
        while not self.game_copy.is_game_over():  # checks the state for game over boolean and loops if it's false

            actions=self.game_copy.get_legal_actions() 
            legal_actions = actions[0] # get legal moves
            player = actions[1] # get player

            action = legal_actions[np.random.randint(len(legal_actions))] # take a random action from legal moves
            
            self.game_copy.update_game(action, player) # takes action just pulled at random
        
        scores = self.game_copy.game_result()
        return scores


    def _backpropogate(self, scores, node):
        """
        Node statistics are updated starting with rollout node and moving up, until the parent node is reached.

        win stats/scores/etc are incremented/decremented for node owner as needed

        Args:
            scores (dict): dictionary of scores with player ID as keys
            node (object instance): MonteCarloNode object instance
        """               
        owner = node.player_owner
        node.number_of_visits += 1  # updates self with number of visits
        # updates self with reward (sent in from _backpropogate)
        node.total_score += scores[owner]

        if node.parent:  # if this node has a parent,
            # call _backpropogate on the parent, so this will continue until root note which has no parent
            self._backpropogate(scores, node.parent)


class MonteCarloNode():


    def __init__(self, parent=None, node_action=None, label='Root Node', depth=0, player=None): #, legal_actions=None
        """
        Initializes monte carlo node

        Args:
            parent (object instance, optional): Node object that spawned this node. Defaults to None.
            node_action (int or str, optional): Action this node returns to game state when node is activated. Defaults to None.
            label (str, optional): Node label for GUI reporting. Defaults to 'Root Node'.
            depth (int, optional): Depth of node in tree. Defaults to 0.
            player (int, optional): Player ID of node owner. Defaults to None.
        """        

        self.parent = parent # the node that spawned this node. Root is None.
        self.node_action = node_action # the action being taken at this node
        self.children = [] # the storage for the children of this node
        self.number_of_visits = 0  # number of times current node is visited
        self.total_score = 0 # total score for this node ONLY for its owner
        self.label = label # label for the node, is used in GUI reporting
        self.depth = depth # depth of the node
        self.player_owner = player # the player who owns/plays this node layer. Should be same player at any given depth.
        return

    def best_child(self, c_param=np.sqrt(2), print_weights=False):
        """
        Evaluates all available children for highest scoring child node
        first param is exploitation and second is exploration

        Args:
            c_param (int, optional): Exploration term. Defaults to root 2.
            print_weights (bool, optional): Will print scores of all child nodes. Defaults to False.

        Returns:
            child node (object instance): MonteCarloNode object instance
        """        
        choices_weights = [] # makes a list to store the score calculations

        for c in self.children:
            try:
                # get scores of all child nodes
                score = (c.total_score / c.number_of_visits) + c_param * (np.sqrt(np.log(self.number_of_visits) / c.number_of_visits))
                choices_weights.append(score)
            except:
                # if calculation runs into a divide by 0 error because child has never been visted
                score=1000
                choices_weights.append(1000)
            
            if print_weights==True:
                # if toggled, will print score for each child
                print(c.depth, c.label, score, c)

        return self.children[np.argmax(choices_weights)] # gets index of max score and sends back identity of child


players = int(sys.argv[2])
game = GameEngine(players)

#print(sys.argv)
game.play_game_byturns(simulations = int(sys.argv[1]))#5556
