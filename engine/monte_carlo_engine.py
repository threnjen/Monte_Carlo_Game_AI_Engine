import numpy as np
import copy

from engine.monte_carlo_node import MonteCarloNode
from games.base_game_object import BaseGameObject


class MonteCarloEngine:
    def __init__(
        self, start_player: int, verbose: bool
    ):  # , legal_actions=None, player=None
        """
        Instantiates root monte carlo node
        Assigns starting player to root node

        Args:
            node_player (int): Current player id
        """
        self.root = MonteCarloNode(player=start_player)
        self.verbose = verbose

    def get_node_action(self, node: MonteCarloNode) -> str:
        return node.node_action

    def sim_turn_select_best_node(
        self,
        num_sims: int,
        game: BaseGameObject,
        node_player: int,
        incoming_node: MonteCarloNode,
    ) -> MonteCarloNode:
        """
        Receives a specific game state from which to make a move

        Runs a given number of simulations, according to the Monte Carlo schema:
        1. Find next node to rollout (_selection_rollout_node)
        2. Expands nods as needed (_expand_new_nodes, from _selection_rollout_node)
        3. Simulate game to terminus (_rollout_from_selected_node)
        4. Back-update scores starting with rollout node (_backpropogate_node_scores)

        Returns the chosen turn action for the game state it was provided

        Args:
            num_sims (int): number of simulations to run for turn
            game (object instance): game logic object instance
            node_player (int): current player ID
            current_node (object instance): current MonteCarloNode object instance

        Returns:
            selected_node (object instance): MonteCarloNode object instance
        """
        for i in range(num_sims):
            if self.verbose:
                print(f"\nSimulation {i}")

            self.game_copy = self._copy_game_state_for_sim(game)

            while not self.game_copy.is_game_over():

                rollout_node = self._selection_rollout_node(incoming_node, node_player)
                if self.verbose:
                    print(
                        f"Rollout node selected: {rollout_node.depth}, {rollout_node.label}, {rollout_node}"
                    )

                self._rollout_from_selected_node()

                if self.verbose:
                    print(self.scores)

                self._backpropogate_node_scores(rollout_node)

        selected_node = self._get_best_move_child_node(incoming_node, real_move=True)

        return selected_node

    def _copy_game_state_for_sim(self, game: BaseGameObject) -> BaseGameObject:
        """copy the game state to test rollout"""
        return copy.deepcopy(game)

    def _selection_rollout_node(
        self, node: MonteCarloNode, node_player: int
    ) -> MonteCarloNode:
        """
        Selects node to run simulation. Is looking for the furthest terminal node to roll out.

        Returns:
            current_node (object instance): MonteCarloNode object instance
        """
        actions = self.game_copy.get_available_actions()

        while len(node.children) > 0 and node.number_of_visits > 0:
            # HAS CHILDREN, IS VISITED, CHECK GAME END AFTER LOOP
            node = self._move_to_node(node, node_player)
            if self.game_copy.is_game_over():
                return node
            actions = self.game_copy.get_available_actions()
            node_player = self.game_copy.get_current_player()
            # loop and check again if we hit a leaf; this branch may move more than one node down to find a new expansion point

        if len(actions) == 0:
            # NO CHILDREN, IS VISITED, means game is over
            return node

        elif node.number_of_visits == 0 and not node == self.root:
            # NO CHILDREN, NOT VISITED, NOT ROOT
            self._expand_new_nodes(node)
            return node

        elif (
            len(node.children) == 0
            and node.number_of_visits > 0
            and not node == self.root
        ):
            # NO CHILDREN, IS VISITED, NOT ROOT
            self._expand_new_nodes(node)
            node = self._move_to_node(node, node_player)
            return node

        elif node.number_of_visits == 0 and node == self.root:
            # NO CHILDREN, NOT VISITED, IS ROOT
            self._expand_new_nodes(node)
            node = self._move_to_node(node, node_player)
            return node

        else:
            return node

    def _get_best_move_child_node(
        self, current_node: MonteCarloNode, real_move=False
    ) -> MonteCarloNode:
        """Calls BEST_CHILD for the node we started on"""
        best_child_node = current_node.best_child(
            real_move=real_move, print_weights=True
        )
        return best_child_node

    def _move_to_node(self, node: MonteCarloNode, player: int) -> MonteCarloNode:
        best_node = self._get_best_move_child_node(node)
        self.game_copy.update_game_with_action(self.get_node_action(best_node), player)
        return best_node

    def _choose_random_action(self, potential_actions: list, type=None):
        if type == "expansion":
            # pops off node actions randomly so that the order of try-stuff isn't as deterministic
            random_end = len(potential_actions)
            action = potential_actions[np.random.randint(random_end)]
        if type == "rollout":
            random_end = len(potential_actions)
            action = potential_actions[
                np.random.randint(random_end)
            ]  # take a random action from legal moves

        return action

    def _expand_new_nodes(self, node: MonteCarloNode):
        """
        From the present state we _expand_new_nodes the nodes to the next possible states
        We take in a node with no children and we will _expand_new_nodes it to all children

        For each available action for the current node, add a new state to the tree

        Query the game state for all of the legal actions, and store that in a list
        As we pop items off the list and apply them to the
        """

        actions_to_pop = self.game_copy.get_available_actions()
        current_player = self.game_copy.get_current_player()

        while len(actions_to_pop) != 0:
            popped_action = self._choose_random_action(
                potential_actions=actions_to_pop, type="expansion"
            )
            actions_to_pop.remove(popped_action)  # pops off an untried action

            # make the child node for the popped action:
            child_node = MonteCarloNode(
                parent=node,
                node_action=popped_action,
                label=f"Action {popped_action}",
                depth=(node.depth + 1),
                player=current_player,
            )

            node.children.append(
                child_node
            )  # appends this new child node to the current node's list of children

    def _rollout_from_selected_node(self):
        """
        On _rollout_from_selected_node call, the entire game is simulated to terminus and the outcome of the game is returned

        Returns:
            scores (dict): dictionary of scores with player ID as keys
        """

        while not self.game_copy.is_game_over():

            legal_actions = self.game_copy.get_available_actions(special_policy=True)
            current_player = self.game_copy.get_current_player()

            random_action = self._choose_random_action(
                potential_actions=legal_actions, type="rollout"
            )
            if self.verbose:
                print(f"Rollout: {current_player} {random_action}")

            self.game_copy.update_game_with_action(
                random_action, current_player
            )  # takes action just pulled at random

        if self.verbose:
            print("game is over, rollout ends")
        self.scores = self.game_copy.get_game_scores()

    def _update_node(self):
        """_summary_"""
        self.node.number_of_visits += 1  # updates self with number of visits
        self.node.total_score += self.scores[self.node.player_owner]

    def _backpropogate_node_scores(self, node: MonteCarloNode):
        """
        Node statistics are updated starting with rollout node and moving up, until the parent node is reached.

        win stats/scores/etc are incremented/decremented for node owner as needed

        Args:
            scores (dict): dictionary of scores with player ID as keys
            node (object instance): MonteCarloNode object instance
        """
        self.node = node

        self._update_node()

        # print("Updated node "+str(node.depth)+str(self.get_node_action(best_node))+" with score of "+str(scores[owner])+', new score is '+str(node.total_score)+'and avg is '+str(node.total_score/node.number_of_visits))

        if self.node.parent:  # if this node has a parent,
            # call _backpropogate_node_scores on the parent, so this will continue until root note which has no parent
            self._backpropogate_node_scores(self.node.parent)
