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
    def actions_required_this_round(self) -> int:
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

    @property
    def all_round_actions_collected(self) -> bool:
        """A boolean to determine if all players have programmed their actions for the round."""
        return len(self.round_actions) == self.actions_required_this_round * len(self.human_player_count)

    def get_available_actions(self, special_policy: bool = False) -> list[DungeonCrawlerAction]:
        """This is the function that the game will call to get the available actions for the current player.
        There are two possibilities:
            - The player is programming their actions for the round.  In this case, the player will be able to
            choose from a list of card permutations.
            - The player is choosing a direction to enact their chosen action.  They need the battle grid to
            determine adjacent empty and occupied squares."""
        if not self.all_round_actions_collected:
            return self.current_player.get_available_actions(self.actions_required_this_round)
        else:
            return self.current_player.get_available_directions(self.battle_grid)

    def update_game_with_action(self, action: DungeonCrawlerAction) -> None:
        if not self.all_round_actions_collected:
            self.round_actions.append(action)
            return
        # Something about this feels wrong.
        # I think the right move is to pass the action to the player, and let the player
        # decide what to do with it.
        if action.type == "move":
            self.current_player.move(action)
        elif action.type == "attack":
            self.current_player.attack(action, self.actors)
        elif action.type =="defend":
            self.current_player.defend(action)
        elif action.type == "recover":
            self.current_player.recover(action)


    def is_game_over(self) -> bool:
        pass

    def draw_board(self) -> None:
        pass

    def save_game_state(self) -> None:
        pass

    def load_save_game_state(self, dict) -> None:
        pass
