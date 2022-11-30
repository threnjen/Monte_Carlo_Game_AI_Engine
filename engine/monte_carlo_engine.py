import numpy as np
import copy

from engine.monte_carlo_node import MonteCarloNode
from games.base_game_object import BaseGameObject
from engine.monte_carlo_tree import MonteCarloTree


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
        self.tree = MonteCarloTree()
        self.root = MonteCarloNode(player=start_player, game_state="Root", game_image="Root")
        self.tree.add_mc_node(self.root)
        self.verbose = verbose
        self.game: BaseGameObject = None

    def update_action_log_start(
        self, node: MonteCarloNode, sim_num: int, node_player: str
    ):
        self.turn_action_log = {}
        self.turn_action_log["Game Turn"] = node.get_depth()
        self.turn_action_log["Sim Number"] = sim_num
        self.turn_action_log["Node Owner"] = node_player

    def update_action_log_node(self, node: MonteCarloNode, label: str, all=True):
        if all:
            self.turn_action_log[f"{label} Node"] = id(node)
        self.turn_action_log[f"{label} Node Score"] = node.get_total_score()
        self.turn_action_log[f"{label} Node Visits"] = node.get_visit_count()
        if all:
            self.turn_action_log[f"{label} Parent Nodes"] = id(
                self.tree.get_parents(node)
            )
            # I need to figure this out a little later
            # self.turn_action_log[f"{label} Node Action"] = node
            self.turn_action_log[f"{label} Node # Children"] = len(
                self.tree.get_children(node)
            )
            self.turn_action_log[f"{label} Node Children"] = [
                id(child) for child in self.tree.get_children(node)
            ]

    def update_action_log_end(self):
        self.turn_action_log["Rollout Score"] = self.scores

    def sim_turn_select_best_node(
        self,
        num_sims: int,
        game: BaseGameObject,
        node_player: int,
        parent: MonteCarloNode,
    ) -> tuple[MonteCarloNode, list[str]]:
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
        self.game = game

        def weighted_score(parent: MonteCarloNode, child: MonteCarloNode):
            try:
                score = (child.get_total_score() / child.get_visit_count()) + 1.414 * (
                    np.sqrt(np.log(parent.get_visit_count()) / child.get_visit_count())
                )
                return round(score, 5)
            except:
                return 1000

        def explore_term(parent: MonteCarloNode, child: MonteCarloNode):
            try:
                return round(
                    1.414
                    * np.sqrt(
                        np.log(parent.get_visit_count()) / child.get_visit_count()
                    ),
                    5,
                )
            except:
                return 1000

        deep_game_log = []

        print(
            f"Incoming node: {id(parent)} Visits: {parent.get_visit_count()} Score: {parent.get_total_score()} "
        )
        nodes = [
            {
                id(child): [
                    child.get_visit_count(),
                    child.get_total_score(),
                    round(child.get_total_score() / child.get_visit_count(), 4),
                    weighted_score(parent, child),
                    explore_term(parent, child),
                ]
            }
            for child in self.tree.get_children(parent)
        ]
        print(f"{nodes}\n")
        original_game_state = self.game.get_game_state()
        for i in range(num_sims):

            self.update_action_log_start(parent, i, node_player)
            self.update_action_log_node(parent, "Starting")

            self.game.update_game_state(original_game_state)

            rollout_node = self._select_rollout_node(parent, node_player)

            self.update_action_log_node(rollout_node, "Rollout")

            self._rollout_from_selected_node()

            self.scores = self.game.get_game_scores()
            self.update_action_log_end()

            self._backpropogate_node_scores(parent, rollout_node)

            self.update_action_log_node(rollout_node, "Rollout After", all=False)

            deep_game_log.append(self.turn_action_log)
            del self.turn_action_log

        selected_child = self.tree.get_best_child(parent, real_move=True)
        self.game.update_game_state(original_game_state)
        nodes = [
            {
                id(child): [
                    child.get_visit_count(),
                    child.get_total_score(),
                    round(child.get_total_score() / child.get_visit_count(), 4),
                    weighted_score(parent, child),
                    explore_term(parent, child),
                ]
            }
            for child in self.tree.get_children(parent)
        ]
        print("End node scores after simulations")
        print(nodes)
        print(
            f"Chosen Node: {id(selected_child)} Visits: {selected_child.get_visit_count()} Score: {selected_child.get_total_score()} "
        )
        print(f"Action taken: {node_player}, {self.tree.get_action(parent_node=parent, child_node=selected_child)}")

        return selected_child, self.tree.get_action(parent_node=parent, child_node=selected_child), deep_game_log

    def _copy_game_state_for_sim(self, game: BaseGameObject) -> BaseGameObject:
        """copy the game state to test rollout"""
        return copy.deepcopy(game)

    def _select_rollout_node(
        self, node: MonteCarloNode, node_player: int
    ) -> MonteCarloNode:
        """
        Selects node to run simulation. Is looking for the furthest terminal node to roll out.

        Returns:
            current_node (object instance): MonteCarloNode object instance
        """

        while len(self.tree.get_children(node)) > 0 and node.get_visit_count() > 0:
            # HAS CHILDREN, IS VISITED, CHECK GAME END AFTER LOOP
            node = self._move_to_best_child_node(node, node_player)
            if self.game.is_game_over():
                return node
            node_player = self.game.get_current_player()
            # loop and check again if we hit a leaf; this branch may move more than one node down to find a new expansion point

        if len(self.game.get_available_actions()) == 0:
            # NO CHILDREN, IS VISITED, means game is over
            return node

        elif node.get_visit_count() == 0 and not node == self.root:
            # NO CHILDREN, NOT VISITED, NOT ROOT
            node = self._expand_new_nodes(node)
            return node

        elif (
            len(self.tree.get_children(node)) == 0
            and node.get_visit_count() > 0
            and not node == self.root
        ):
            # NO CHILDREN, IS VISITED, NOT ROOT
            node = self._expand_new_nodes(node)
            node = self._move_to_best_child_node(node, node_player)
            return node

        elif node.get_visit_count() == 0 and node == self.root:
            # NO CHILDREN, NOT VISITED, IS ROOT
            node = self._expand_new_nodes(node)
            node = self._move_to_best_child_node(node, node_player)
            return node

        else:
            return node

    def _move_to_best_child_node(
        self, parent: MonteCarloNode, player: int
    ) -> MonteCarloNode:
        best_child = self.tree.get_best_child(parent)
        self.game.update_game_with_action(self.tree.get_action(parent, best_child), player)
        return best_child

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

    def _expand_new_nodes(self, parent_node: MonteCarloNode):
        """
        From the present state we _expand_new_nodes the nodes to the next possible states
        We take in a node with no children and we will _expand_new_nodes it to all children

        For each available action for the current node, add a new state to the tree

        Query the game state for all of the legal actions, and store that in a list
        As we pop items off the list and apply them to the
        """

        actions_to_pop = self.game.get_available_actions()
        current_player = self.game.get_current_player()
        game_state_before_action = self.game.get_game_state()
        for action in actions_to_pop:
            # make the child node for the popped action:
            self.game.update_game_state(game_state_before_action)
            self.game.update_game_with_action(action, current_player)
            child_node = MonteCarloNode(
                label=self.game.get_game_state(),
                depth=(parent_node.get_depth() + 1),
                player=current_player,
                game_state=self.game.get_game_state(),
                game_image=self.game.draw_board()
            )

            self.tree.add_child_node(parent_node, child_node, action)
        return parent_node

    def _rollout_from_selected_node(self):
        """
        On _rollout_from_selected_node call, the entire game is simulated to terminus and the outcome of the game is returned

        Returns:
            scores (dict): dictionary of scores with player ID as keys
        """

        rollout = 1
        while not self.game.is_game_over():

            legal_actions = self.game.get_available_actions(special_policy=True)
            current_player = self.game.get_current_player()

            random_action = self._choose_random_action(
                potential_actions=legal_actions, type="rollout"
            )

            self.game.update_game_with_action(
                random_action, current_player
            )  # takes action just pulled at random
            rollout += 1

    def _backpropogate_node_scores(self, starting_node: MonteCarloNode, ending_node: MonteCarloNode):
        """
        Node statistics are updated starting with rollout node and moving up, until the parent node is reached.

        win stats/scores/etc are incremented/decremented for node owner as needed

        Args:
            scores (dict): dictionary of scores with player ID as keys
            node (object instance): MonteCarloNode object instance
        """

        ancestors = self.tree.get_nodes_path(starting_node, ending_node)
        for ancestor in ancestors:
            ancestor.add_to_visits(1)
            ancestor.add_to_score(self.scores[ancestor.get_node_owner()])
