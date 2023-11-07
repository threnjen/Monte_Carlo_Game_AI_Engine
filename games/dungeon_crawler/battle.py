from typing_extensions import Unpack
from pydantic.config import ConfigDict
from game_components.base_game_object import BaseGameObject
from .battle_grid import BattleGrid
from pydantic import field_validator, Field
from action import DungeonCrawlerAction
import numpy as np

class Battle(BaseGameObject):
    actors: dict
    current_player_num: int = 0
    save_game: dict = None
    battle_grid: BattleGrid = Field(default_factory=BattleGrid, validate_default=True)
    round_actions: list[DungeonCrawlerAction] = None


    @field_validator("battle_grid")
    def create_battle_grid(self):
        if self.battle_grid is None:
            self.battle_grid = BattleGrid()

    @property
    def human_player_count(self):
        return len([actor for actor in self.actors.values() if actor.type == "human"])

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
        pass


    @property
    def current_player(self):
        return self.players[self.current_player_num]

    def get_available_actions(self, special_policy: bool = False) -> list:
        pass

    # def get_adjacent_targets(self, actor_num: int) -> list:
    #     adjacent_squares = self.battle_grid.get_adjacent_squares(actor_num)
    #     return [self.battle_grid.get_actor(square) for square in adjacent_squares]

    def get_distance(self, position1, position2) -> int:
        indices_element1 = np.argwhere(my_2d_array == position1)  # Get the indices of element1
        indices_element2 = np.argwhere(my_2d_array == element2)  # Get the indices of element2

        if indices_element1.size > 0 and indices_element2.size > 0:
            position1 = indices_element1[0]
            position2 = indices_element2[0]
            positional_difference = np.abs(position2 - position1)

    def update_game_with_action(self, action) -> None:
        if len(self.round_actions) < self.actions_this_round * len(self.human_player_count):
            self.round_actions.append(action)
            return
        self.current_player.

    def is_game_over(self) -> bool:
        pass

    def draw_board(self) -> None:
        pass

    def save_game_state(self) -> None:
        pass

    def load_save_game_state(self, dict) -> None:
        pass
