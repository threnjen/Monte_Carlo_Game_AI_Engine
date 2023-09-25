from pydantic import BaseModel
from games.game_components.game import GameEnvironment

class Player(BaseModel):
    model_config = {"arbitrary_types_allowed": True}
    player_number: int
    player_score: int
    first_player: bool
    choose_action: callable

    def get_available_actions(self, special_policy: bool = False) -> list:
        pass

    def take_action(self, action: list[float], game_object: GameEnvironment):
        pass

    def get_action_choice(self, action_list: list) -> list:
        chosen_action = None
        while chosen_action not in action_list:
            chosen_action = self.choose_action(action_list)
        return chosen_action
