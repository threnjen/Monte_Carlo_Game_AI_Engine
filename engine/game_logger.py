from engine.monte_carlo_node import MonteCarloNode


class GameLogger:
    def __init__(self) -> None:
        self.turn_action_log = {}

    def create_turn_action_log(self):
        del self.turn_action_log
        self.turn_action_log = {}

    def update_action_log_start(self, node: MonteCarloNode, sim_num: int, node_player: str):
        self.turn_action_log["Game Turn"] = node.depth
        self.turn_action_log["Sim Number"] = sim_num
        self.turn_action_log["Node Owner"] = node_player

    def update_action_log_node(self, node: MonteCarloNode, label: str, all=True):
        if all:
            self.turn_action_log[f"{label} Node"] = id(node)
        self.turn_action_log[f"{label} Node Score"] = node.total_score
        self.turn_action_log[f"{label} Node Visits"] = node.number_of_visits
        if all:
            self.turn_action_log[f"{label} Parent Node"] = id(node.parent)
            self.turn_action_log[f"{label} Node Action"] = node.node_action
            self.turn_action_log[f"{label} Node # Children"] = len(node.children)
            self.turn_action_log[f"{label} Node Children"] = [id(child) for child in node.children]

    def send_turn_action_log(self):
        return self.turn_action_log

    def update_action_log_end(self, scores):
        self.turn_action_log["Rollout Score"] = scores
