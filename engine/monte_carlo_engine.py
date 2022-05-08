import numpy as np
import copy

from .monte_carlo_node import MonteCarloNode

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
            
            print("\nSimulation "+str(i))
            # COPY THE GAME STATE HERE AND ROLL OUT ON IT NOT THE REAL GAME
            self.game_copy = copy.deepcopy(game)

            while not self.game_copy.is_game_over(): # for as long as the copied game is not over:
                
                self.rollout_node = self._selection(self.current_node, current_player) # call _selection to find the node to roll out, taking the moves along the way
                print("Rollout node selected: "+str(self.rollout_node.depth)+str(self.rollout_node.label)+str(self.rollout_node))

                self.scores = self._rollout() # call _rollout to finish simulating the game
                print(self.scores)

                #print("Scores before backpropogation:")
                #test = self.current_node.best_child(print_weights=True)
                self._backpropogate(self.scores, self.rollout_node) # _backpropogates with the scores starting from the rollout_node
                #print("Scores after backpropogation:")
                #test = self.current_node.best_child(print_weights=True)

        # Simulations have finished running, time to get the best move and return it to the game engine
        print("Exit state")
        selected_node = self.current_node.best_child(print_weights=True, real_decision=True) # Calls BEST_CHILD for the node we started on

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
        print("Selection")
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
            # CHECK GAME END AFTER LOOP
            print(str(current_node.label)+"Not leaf, moving down")
            current_node = current_node.best_child(print_weights=False) # change the current node to the best child
            move_node(current_node, self.player) # take the move of the new current node
            if self.game_copy.is_game_over==True:
                return current_node
            self.player=self.game_copy.get_legal_actions(policy=False)[1]
            # loop and check again if we hit a leaf; this branch may move more than one node down to find a new expansion point
  
        # Now we have reached a leaf node

        if len(self.game_copy.get_legal_actions(policy=False)[0])==0:
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

        else: return current_node

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
        print("Expansion")
        actions_to_pop=self.game_copy.get_legal_actions(policy=False)[0] # call to get legal moves. Calls GET_LEGAL_ACTIONS in GameLogic

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

            actions=self.game_copy.get_legal_actions(policy=False) 
            legal_actions = actions[0] # get legal moves
            player = actions[1] # get player

            action = legal_actions[np.random.randint(len(legal_actions))] # take a random action from legal moves
            
            print("Rollout: "+str(player)+str(action))

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

        print("Updated node "+str(node.depth)+str(node.node_action)+" with score of "+str(scores[owner])+', new score is '+str(node.total_score)+'and avg is '+str(node.total_score/node.number_of_visits))


        #if scores[owner] > 0:
        #    node.total_score += scores[owner]
        #elif scores[owner] == 0:
        #    node.total_score += .5
        #else: pass

        if node.parent:  # if this node has a parent,
            # call _backpropogate on the parent, so this will continue until root note which has no parent
            self._backpropogate(scores, node.parent)



