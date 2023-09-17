import networkx as nx
import pylab as plt

# from networkx.drawing.nx_agraph import write_dot, graphviz_layout
import networkx as nx
from engine.monte_carlo_node import MonteCarloNode
import numpy as np

IMAGE = "image"
MC_NODE = "mc_node"
ACTION_ID = "action_id"


class MonteCarloTree(nx.DiGraph):
    def draw_graph(self):
        nx.draw(self, with_labels=False, arrows=True)
        plt.show()

    def add_mc_node(self, new_node: MonteCarloNode):
        self.add_nodes_from(
            [
                (
                    new_node.get_game_state(),
                    {IMAGE: new_node.get_game_image(), MC_NODE: new_node},
                )
            ]
        )

    def add_child_node(
        self, parent_node: MonteCarloNode, child_node: MonteCarloNode, action
    ):
        if child_node.get_game_state() not in self:
            self.add_mc_node(child_node)
        self.add_edge(
            parent_node.get_game_state(),
            child_node.get_game_state(),
            node_action=action,
        )

    def get_ancestors(self, node: MonteCarloNode) -> list[MonteCarloNode]:
        return [
            self.nodes[ancestor][MC_NODE]
            for ancestor in nx.ancestors(self, node.get_game_state())
        ]

    def get_children(self, parent_node: MonteCarloNode) -> list[MonteCarloNode]:
        return [
            self.nodes[child][MC_NODE]
            for child in self.successors(parent_node.get_game_state())
        ]

    def get_parents(self, child_node: MonteCarloNode) -> list[MonteCarloNode]:
        return [
            self.nodes[parent][MC_NODE]
            for parent in self.predecessors(child_node.get_game_state())
        ]

    def get_best_child(
        self, parent_node: MonteCarloNode, explore_param=1.414, real_move=False
    ) -> MonteCarloNode:
        choices_weights = []  # makes a list to store the score calculations
        for child in self.get_children(parent_node):
            try:
                # get scores of all child nodes
                if real_move:
                    score = child.get_visit_count()
                else:
                    score = (
                        child.get_total_score() / child.get_visit_count()
                    ) + explore_param * (
                        np.sqrt(
                            np.log(parent_node.get_visit_count())
                            / child.get_visit_count()
                        )
                    )
                choices_weights.append(score)
            except:
                # if calculation runs into a divide by 0 error because child has never been visted
                score = 1e6
                choices_weights.append(1e6)
        if max(choices_weights) > 1e6:
            pass
        return self.get_children(parent_node)[np.argmax(choices_weights)]

    def get_action(
        self, parent_node: MonteCarloNode, child_node: MonteCarloNode
    ) -> str:
        return self[parent_node.get_game_state()][child_node.get_game_state()][
            "node_action"
        ]

    def get_nodes_path(self, parent: MonteCarloNode, child: MonteCarloNode) -> list[MonteCarloNode]:
        shortest_path = nx.shortest_path(self, parent.get_game_state(), child.get_game_state())
        return [self.nodes[node][MC_NODE] for node in shortest_path]
