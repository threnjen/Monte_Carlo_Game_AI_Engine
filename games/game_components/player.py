from pydantic import BaseModel

class Player(BaseModel):
    model_config = {"arbitrary_types_allowed": True}
    player_number: int
    player_score: int = 0
    first_player: bool = False
    choose_action: callable = None

    def get_action_choice(self, action_list: list) -> list:
        chosen_action = None
        while chosen_action not in action_list:
            chosen_action = self.choose_action(action_list)
        return chosen_action
