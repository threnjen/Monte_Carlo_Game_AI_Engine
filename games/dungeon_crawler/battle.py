from typing_extensions import Unpack
from pydantic.config import ConfigDict
from game_components.base_game_object import BaseGameObject, field_validator
from .battle_grid import BattleGrid

class Battle(BaseGameObject):
    actors: dict
    current_player_num: int = 0
    save_game: dict = None
    battle_grid: BattleGrid = None


    @field_validator
    def create_battle_grid(self):
        if self.battle_grid is None:
            self.battle_grid = BattleGrid()

    def set_round_order(self):
        self.actors = dict(sorted(self.actors.items(), key=lambda x: x[1].initiative))

    @property
    def actions_this_round(self) -> int:
        """The game needs to know the number of actions each actor will be able to program.
        Right now, this is dictated by the undead actors, and is the max among those undead
        actors."""
        return max([actor.round_actions for actor in self.actors.values() if actor.type == "undead"])

    def play_round_actions(self):
        """ I'm having a lot of trouble with this one. The problem is that after the
        actions are chosen, a direction needs to be chosen.  However, this means
        we can't just play out the whole round without getting more input from the player."""
                    

    @property
    def current_player(self):
        return self.players[self.current_player_num]

    def get_available_actions(self, special_policy: bool = False) -> list:
        pass

    def update_game_with_action(self, action: str, player: int) -> None:
        pass

    def is_game_over(self) -> bool:
        pass

    def draw_board(self) -> None:
        pass

    def save_game_state(self) -> None:
        pass

    def load_save_game_state(self, dict) -> None:
        pass
