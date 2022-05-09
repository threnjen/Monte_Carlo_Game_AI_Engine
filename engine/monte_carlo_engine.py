import numpy as np
import copy

from engine.monte_carlo_node import MonteCarloNode

class MonteCarloEngine():

    def __init__(self, node_player, verbose): #, legal_actions=None, player=None
        """
        Instantiates root monte carlo node
        Assigns starting player to root node

        Args:
            node_player (int): Current player id
        """          
        self.root = MonteCarloNode(player=node_player)
        self.verbose = verbose

    def play_turn(self, num_sims, game, node_player, received_node):
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
            node_player (int): current player ID
            current_node (object instance): current MonteCarloNode object instance

        Returns:
            selected_node (object instance): MonteCarloNode object instance
        """        
        self.current_node = received_node # set current node to received node
        self.node_player = node_player # set node_player to received player

        for i in range(num_sims):  # Run x simulations for this turn
            
            print("\nSimulation "+str(i))
            
            self.game_copy = copy.deepcopy(game) # COPY THE GAME STATE HERE TO TEST ROLLOUT

            while not self.game_copy.is_game_over():
                
                self.rollout_node = self._selection(self.current_node) # call _selection to find the node to roll out, taking the moves along the way
                print(f"Rollout node selected: {self.rollout_node.depth}, {self.rollout_node.label}, {self.rollout_node}")

                self.scores = self._rollout() # call _rollout to finish simulating the game
                print(self.scores)

                self._backpropogate(self.scores, self.rollout_node) # _backpropogates with the scores starting from the rollout_node

        # Simulations have finished running, time to get the best move and return it to the game engine
        selected_node = self.current_node.best_child(print_weights=True) # Calls BEST_CHILD for the node we started on

        return selected_node # returns the best child node to the main function.

    def _move_node(self, node):
        node = node.best_child(print_weights=False) # get the best child of the root
        self.game_copy.update_game(node.node_action, self.current_player)
        return node

    def _selection(self, node):
        """
        Selects node to run simulation. Is looking for the furthest terminal node to roll out.

        Returns:
            current_node (object instance): MonteCarloNode object instance
        """        

        self.current_player=self.node_player # set temp current player to initial current player

        # Evaluate our incoming node.
        while len(node.children) > 0 and node.number_of_visits > 0: 
            # HAS CHILDREN, IS VISITED, CHECK GAME END AFTER LOOP
            print("HAS CHILDREN, IS VISITED, CHECK GAME END AFTER LOOP")
            node = self._move_node(node)
            if self.game_copy.is_game_over():
                return node
            self.current_player=self.game_copy.get_legal_actions(policy=False)[1]
            # loop and check again if we hit a leaf; this branch may move more than one node down to find a new expansion point

        if len(self.game_copy.get_legal_actions(policy=False)[0])==0:
            print("NO CHILDREN, IS VISITED, means game is over")
            # NO CHILDREN, IS VISITED, means game is over
            return node

        elif node.number_of_visits == 0 and not node == self.root:
            print("NO CHILDREN, NOT VISITED, NOT ROOT")
            # NO CHILDREN, NOT VISITED, NOT ROOT 
            self._expansion(node)
            return node

        elif len(node.children) == 0 and node.number_of_visits > 0 and not node == self.root:
            print("NO CHILDREN, IS VISITED, NOT ROOT")
            # NO CHILDREN, IS VISITED, NOT ROOT
            self._expansion(node)
            node = self._move_node(node)
            return node

        elif node.number_of_visits == 0 and node == self.root:
            # NO CHILDREN, NOT VISITED, IS ROOT
            self._expansion(node)
            node = self._move_node(node)
            return node

        else: return node

    def _expansion(self, node):
        """
        From the present state we _expansion the nodes to the next possible states
        We take in a node with no children and we will _expansion it to all children

        For each available action for the current node, add a new state to the tree

        Query the game state for all of the legal actions, and store that in a list
        As we pop items off the list and apply them to the
        """        
        print("Expansion")
        actions_to_pop=self.game_copy.get_legal_actions(policy=False)[0] # call to get legal moves. Calls GET_LEGAL_ACTIONS in GameLogic

        while len(actions_to_pop) != 0:

            # pops off node actions randomly so that the order of try-stuff isn't as deterministic
            action = actions_to_pop[np.random.randint(len(actions_to_pop))]
            actions_to_pop.remove(action) # pops off an untried action

            # make the child node for the popped action:
            child_node = MonteCarloNode(parent=node, node_action=action, label=f'Action {action}', depth = (node.depth+1), player=self.current_player) 

            node.children.append(child_node) # appends this new child node to the current node's list of children            


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
            
            print(f"Rollout: {player} {action}")

            self.game_copy.update_game(action, player) # takes action just pulled at random
        
        print("game is over, rollout ends")
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

        node.total_score += scores[owner]

        #print("Updated node "+str(node.depth)+str(node.node_action)+" with score of "+str(scores[owner])+', new score is '+str(node.total_score)+'and avg is '+str(node.total_score/node.number_of_visits))

        if node.parent:  # if this node has a parent,
            # call _backpropogate on the parent, so this will continue until root note which has no parent
            self._backpropogate(scores, node.parent)



