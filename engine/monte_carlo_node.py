import numpy as np


class MonteCarloNode:
    def __init__(
        self, parent=None, node_action=None, label="Root Node", depth=0, player=None
    ):  # , legal_actions=None
        """
        Initializes monte carlo node

        Args:
            parent (object instance, optional): Node object that spawned this node. Defaults to None.
            node_action (int or str, optional): Action this node returns to game state when node is activated. Defaults to None.
            label (str, optional): Node label for GUI reporting. Defaults to 'Root Node'.
            depth (int, optional): Depth of node in tree. Defaults to 0.
            player (int, optional): Player ID of node owner. Defaults to None.
        """

        self.parent = parent  # the node that spawned this node. Root is None.
        self.node_action = node_action  # the action being taken at this node
        self.children = []  # the storage for the children of this node
        self.number_of_visits = 0  # number of times current node is visited
        self.total_score = 0  # total score for this node ONLY for its owner
        self.label = label  # label for the node, is used in GUI reporting
        self.depth = depth  # depth of the node
        self.player_owner = player  # the player who owns/plays this node layer. Should be same player at any given depth.

    def best_child(self, c_param=1.414, print_weights=False):
        """
        Evaluates all available children for highest scoring child node
        first param is exploitation and second is exploration

        Args:
            c_param (int, optional): Exploration term. Defaults to root 2.
            print_weights (bool, optional): Will print scores of all child nodes. Defaults to False.

        Returns:
            child node (object instance): MonteCarloNode object instance
        """
        choices_weights = []  # makes a list to store the score calculations

        for c in self.children:
            try:
                # get scores of all child nodes
                score = (c.total_score / c.number_of_visits) + c_param * (
                    np.sqrt(np.log(self.number_of_visits) / c.number_of_visits)
                )
                choices_weights.append(score)
            except:
                # if calculation runs into a divide by 0 error because child has never been visted
                score = 1000
                choices_weights.append(1000)

            # if print_weights==True:
            # if toggled, will print score for each child
            # print(c.depth, c.node_action, c.player_owner, score, c)

        return self.children[
            np.argmax(choices_weights)
        ]  # gets index of max score and sends back identity of child
