# this file is the custom monte carlo framework for our AI to plug into

import numpy as np
import copy
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
        self.start_player = randint(0,players)
        
        for i in range(players):
            self.players[i] = Player()
        
        print("Initializing game for "+str(players)+" players")
        #print(self.start_player)

    def get_legal_moves(self):
        '''
        Hook #1
        report on currently available actions after checking board space
        returns list of actions

        '''
        return self.game.get_legal_moves()

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

    def play_game(self, players):
        '''
        Intializes gameplay
        Will play game until game over condition is met
        Each turn will run a MC for that turn choice
        '''

        self.simulations = 1000
        self.turn = 0

        while not self.game.is_game_over():
            
            for player in range(players):

                print("New Turn. Current board state:")
                print(self.game._state)

                self.turn += 1
                self.sims_this_turn = int(self.simulations/(self.turn * 2))

                legal_actions=self.game.get_legal_actions()

                self.current_turn = TurnEngine(legal_actions, player)
                # sends number of simulations and current game to turn engine
                self.action = self.current_turn.play_turn(
                    self.sims_this_turn, self.game)
                #   gets back the optimal action

                #print("filling: "+str(self.action))

                self.state = self.game.update_game(self.action, player) # updates the true game state with the action

                if self.game.is_game_over():
                    break

            # opponent takes turn. commented out because we don't need that right now.
            #possible_moves = self.game.get_legal_actions()
            #action = possible_moves[np.random.randint(len(possible_moves))]
            #self.state = self.game.update_game(action)

        print("Game over")
        self.scores = self.game.game_result()
        print(self.game._state)
        print(self.scores)


class TurnEngine():

    def __init__(self, legal_actions=None, player=None):
        '''
        Instantiates root monte carlo node
        '''    
        self.root = MonteCarloNode(legal_actions=legal_actions) # parent_action=None, state=self.game._state,
        self.player = player

    def play_turn(self, num_sims, game):
        '''
        Received a specific game state from which to make a move

        Runs a given number of simulations to terminus, according to the Monte Carlo schema:
        1. Find next node to rollout (Expansion)
        2. Rollout game (Simulation)
        3. Backpropogate

        Returns the optimal turn action for the game state it was provided
        '''
        print("Starting turn calculation with "+str(num_sims)+" sims")

        for i in range(num_sims):  # how many simulations with this initial state?

            # COPY THE GAME STATE HERE AND ROLL OUT ON IT NOT THE REAL GAME
            self.game_copy = copy.deepcopy(game)

            rollout_node = self._tree_policy(self.root) # call TREE_POLICY to select the node to rollout. v is a NODE

            # call ROLLOUT on the node v. Starts from node v and takes legal actions until the game ends. Gets the rewards
            reward = self.rollout(self.player)
            #print("Reward: "+str(reward))

            #print(v)
            self.backpropogate(reward, rollout_node) # backpropogates with the reward. Calls BACKPROPOGATE
    
        selected_node = self.root.best_child() # returns the best child node to the main function. Calls BEST_CHILD
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
        while len(current_node.children) == 0:

            #print("Expansion is still possible")

            # check if the current node isn't fully expanded
            while len(current_node._untried_actions) != 0:
                #print("Current node is not fully expanded, expanding node")
                # if not expanded, expand current node
                self.expand(current_node)

        # logic here is only expanding one node no matter what, i think
        # if current node is expanded, find best child
        #print("Current node is fully expanded, getting best child")
        # calls BEST_CHILD to get best scoring leaf
        current_node = current_node.best_child()

        return current_node

    def expand(self, current_node):
        '''
        From the present state we expand the nodes to the next possible states
        '''
        #print("Expanding nodes")
        action = current_node._untried_actions.pop() # pops off an untried action
        self.state = self.game_copy.update_game(action, self.player) # calls move function on the action to get next_state. Calls MOVE in GameLogic object
        child_node = MonteCarloNode(parent=current_node, action_label=action) # parent_action=action, state=next_state,  # instantiates a new node from next state and the action selected
        current_node.children.append(child_node) # appends this new child node to the current node's list of children
        #return child_node

    def rollout(self, player):
        '''
        On rollout call, the entire game is simulated to terminus and the outcome of the game is returned
        '''
        #print("Now entering rollout function")
        while not self.game_copy.is_game_over():  # checks the state for game over boolean and loops if it's false
            #print("Game is not over")

            #print("Getting possible moves")
            possible_moves = self.game_copy.get_legal_actions() # call to get legal moves. Calls GET_LEGAL_ACTIONS in GameLogic object
            #action = self.rollout_policy(possible_moves) # Calls ROLLOUT_POLICY in case needs more complicated
            action = possible_moves[np.random.randint(len(possible_moves))] # call random move from possible moves
            #print(action)
            self.game_copy.update_game(action, player) # takes action just pulled at random. Calls MOVE in GameLogic object

        #print("This simulation has ended; returning result")
        # returns game_result when game is flagged over. Calls GAME_RESULT in GameLogic object
        self.scores = self.game_copy.game_result()
        return self.scores[player]


    def backpropogate(self, reward, node):
        '''
        all node statistics are updated. Until the parent node is reached.
        All visits +1
        win stats/scores/etc are incrememnted as needed
        '''

        #print("Now entering backpropogation function")
        # print(node.number_of_visits)
        # print(node.total_score[0])

        node.number_of_visits += 1  # updates self with number of visits
        # updates self with reward (sent in from backpropogate)
        node.total_score += reward
        #print("Updated self total_score")

        if node.parent:  # if this node has a parent,
            #print("Backpropogating parent node")
            # call backpropogate on the parent, so this will continue until root note which has no parent
            self.backpropogate(reward, node.parent)


class MonteCarloNode():

    # parent_action=None, state=None,
    def __init__(self, parent=None, action_label=None, legal_actions=None):
        # self.state = state # board state, in tic tac toe is 3x3 array. (defined by user)
        # none for the root node and for other nodes is = node derived from. First turn will be none
        self.parent = parent
        # self.parent_action = parent_action # none for root but is = parent action for other nodes
        self.action_label = action_label
        self.children = []  # all possible actions from current node
        self.number_of_visits = 0  # number of times current node is visited
        self.total_score = 0
        self._untried_actions = None
        # call to get legal moves. Calls GET_LEGAL_ACTIONS in GameLogic object
        self._untried_actions = legal_actions
        return

    def node_visits(self):
        # returns number of times that node has been visited
        return self.number_of_visits

    def best_child(self, c_param=3):
        '''
        selects best child node from available array
        first param is exploitation and second is exploration
        '''
        #print("Now in best_child function")
        # makes an array of the leaf calculations
        choices_weights = []
        for c in self.children:
            try:
                score = (c.total_score / c.node_visits()) + c_param * \
                    np.sqrt((np.log(self.node_visits())) / c.node_visits())
                choices_weights.append(score)
            except:
                choices_weights.append(100)

        return self.children[np.argmax(choices_weights)] # gets index of max score and sends back identity of child

class Player():
    def __init__(self):
        self.score = 0

players = 2
game = GameEngine(players)
game.play_game(players)
