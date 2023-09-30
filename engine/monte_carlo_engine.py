import numpy as np

from engine.monte_carlo_node import MonteCarloNode
from games.game_components.base_game_object import BaseGameObject
from engine.game_logger import GameLogger
from games.game_components.action import GameAction


class MonteCarloEngine:
    def __init__(self, start_player: int, verbose: bool):  # , legal_actions=None, player=None
        """
        Instantiates root monte carlo node
        Assigns starting player to root node

        Args:
            node_player (int): Current player id
        """
        self.root = MonteCarloNode(player=start_player)
        self.game_logger = GameLogger()
        self.verbose = verbose

    def select_and_return_best_real_action(
        self,
        num_sims: int,
        game: BaseGameObject,
        node_player: int,
        parent: MonteCarloNode,
    ) -> GameAction:
        """
        Receives a specific game state from which to make a move

        Runs a given number of simulations, according to the Monte Carlo schema:
        1. Find next node to rollout (_select_rollout_node)
        2. Expands nods as needed (_expand_new_nodes, from _select_rollout_node)
        3. Simulate game to terminus (_rollout_from_selected_node)
        4. Back-update scores starting with rollout node (_backpropogate_node_scores)

        Returns the chosen turn action for the game state it was provided

        Args:update_action_log_start
            num_sims (int): number of simulations to run for turn
            game (object instance): game logic object instance
            node_player (int): current player ID
            current_node (object instance): current MonteCarloNode object instance

        Returns:
            selected_node (object instance): MonteCarloNode object instance
        """
        self.turn_player = node_player
        self.game_copy = game

        # deep_game_log = []

        # print(f"Incoming node: {id(parent)} Visits: {parent.number_of_visits} Score: {parent.total_score} ")

        self.game_copy.save_game_state()

        for i in range(num_sims):
            # self.game_logger.create_turn_action_log()
            # self.game_logger.update_action_log_start(parent, i, node_player)
            # self.game_logger.update_action_log_node(parent, "Starting")

            rollout_node = self._select_rollout_node(parent, node_player)

            # self.game_logger.update_action_log_node(rollout_node, "Rollout")

            self._rollout_from_selected_node()

            self.scores = self.game_copy.get_game_scores()
            # self.game_logger.update_action_log_end(scores=self.scores)

            self._backpropogate_node_scores(rollout_node)

            # self.game_logger.update_action_log_node(rollout_node, "Rollout After", all=False)

            # deep_game_log.append(self.game_logger.send_turn_action_log())

            self.game_copy.load_save_game_state()

        selected_child = parent.best_child(real_move=True)

        print(
            f"Chosen Node: {id(selected_child)} Visits: {selected_child.number_of_visits} Score: {selected_child.total_score} "
        )
        print(f"Action taken: Player {node_player}, Action {selected_child.get_action()}")

        return selected_child.get_action()  # , deep_game_log

    def _select_rollout_node(self, node: MonteCarloNode, node_player: int) -> MonteCarloNode:
        """
        Selects node to run simulation. Is looking for the furthest terminal node to roll out.

        Returns:
            current_node (object instance): MonteCarloNode object instance
        """

        while len(node.children) > 0 and node.number_of_visits > 0:
            # HAS CHILDREN, IS VISITED, CHECK GAME END AFTER LOOP
            node = self._move_to_best_child_node(node, node_player)
            if self.game_copy.is_game_over():
                return node
            node_player = self.game_copy.get_current_player()
            # loop and check again if we hit a leaf; this branch may move more than one node down to find a new expansion point

        if len(self.game_copy.get_available_actions()) == 0:
            # NO CHILDREN, IS VISITED, means game is over
            return node

        elif node.number_of_visits == 0 and not node == self.root:
            # NO CHILDREN, NOT VISITED, NOT ROOT
            node = self._expand_new_nodes(node)
            return node

        elif len(node.children) == 0 and node.number_of_visits > 0 and not node == self.root:
            # NO CHILDREN, IS VISITED, NOT ROOT
            node = self._expand_new_nodes(node)
            node = self._move_to_best_child_node(node, node_player)
            return node

        elif node.number_of_visits == 0 and node == self.root:
            # NO CHILDREN, NOT VISITED, IS ROOT
            node = self._expand_new_nodes(node)
            node = self._move_to_best_child_node(node, node_player)
            return node

        else:
            return node

    def _move_to_best_child_node(self, parent: MonteCarloNode, player: int) -> MonteCarloNode:
        best_child = parent.best_child()
        self.game_copy.update_game_with_action(best_child.node_action, player)
        return best_child

    def _choose_random_action(self, potential_actions: list):
        # pops off node actions randomly so that the order of try-stuff isn't as deterministic
        random_end = len(potential_actions)
        action = potential_actions[np.random.randint(random_end)]

        return action

    def _expand_new_nodes(self, parent_node: MonteCarloNode):
        """
        From the present state we _expand_new_nodes the nodes to the next possible states
        We take in a node with no children and we will _expand_new_nodes it to all children

        For each available action for the current node, add a new state to the tree

        Query the game state for all of the legal actions, and store that in a list
        As we pop items off the list and apply them to the
        """

        actions_to_pop = self.game_copy.get_available_actions()
        current_player = self.game_copy.get_current_player()

        for action in actions_to_pop:
            # make the child node for the popped action:
            child_node = MonteCarloNode(
                parent=parent_node,
                node_action=action,
                label=f"Action {action}",
                depth=(parent_node.depth + 1),
                player=current_player,
            )

            parent_node.children.append(
                child_node
            )  # appends this new child node to the current node's list of children
        return parent_node

    def _rollout_from_selected_node(self):
        """
        On _rollout_from_selected_node call, the entire game is simulated to terminus and the outcome of the game is returned

        Returns:
            scores (dict): dictionary of scores with player ID as keys
        """

        rollout = 1
        while not self.game_copy.is_game_over():
            legal_actions = self.game_copy.get_available_actions(special_policy=True)
            current_player = self.game_copy.get_current_player()

            random_action = self._choose_random_action(potential_actions=legal_actions)

            self.game_copy.update_game_with_action(random_action, current_player)  # takes action just pulled at random
            rollout += 1

    def _backpropogate_node_scores(self, child_node: MonteCarloNode):
        """
        Node statistics are updated starting with rollout node and moving up, until the parent node is reached.

        win stats/scores/etc are incremented/decremented for node owner as needed

        Args:
            scores (dict): dictionary of scores with player ID as keys
            node (object instance): MonteCarloNode object instance
        """

        # if self.turn_action_log == node.player_owner:
        for ancestor in child_node.get_ancestors():
            ancestor.number_of_visits += 1
            ancestor.total_score += self.scores[ancestor.player_owner]