from typing_extensions import Unpack
from pydantic.config import ConfigDict
from game_components.base_game_object import BaseGameObject
from .battle_grid import BattleGrid
from pydantic import field_validator, Field
from action import DungeonCrawlerAction
import numpy as np
from typing import ClassVar

class Battle(BaseGameObject):
    _HUMAN: ClassVar[str] = "human"
    _UNDEAD: ClassVar[str] = "undead"
    actors: dict
    current_actor_num: int = 0
    save_game: dict = None
    battle_grid: BattleGrid = Field(default_factory=BattleGrid, validate_default=True)
    round_actions: list[DungeonCrawlerAction] = None
    human_players: dict = None
    monsters: dict = None
    round_num: int = 0

    @field_validator("battle_grid")
    def create_battle_grid(self):
        if self.battle_grid is None:
            self.battle_grid = BattleGrid()

    @field_validator("human_players")
    def create_human_players(self):
        if self.human_players is None:
            self.human_players = {name: actor for name, actor in self.actors.items() if actor.type == self._HUMAN}

    @field_validator("monsters")
    def create_monsters(self):
        if self.monsters is None:
            self.monsters = {name: actor for name, actor in self.actors.items() if actor.type == self._UNDEAD}

    @field_validator(round_num):
    def create_round_num(self):
        if self.round_num == 0:
            self.round_num = 1
            self.start_round()

    @property
    def human_player_count(self):
        return len([actor for actor in self.actors.values() if actor.type == self._HUMAN])

    def set_round_order(self):
        self.actors = dict(sorted(self.actors.items(), key=lambda x: x[1].initiative))

    @property
    def actions_required_this_round(self) -> int:
        """The game needs to know the number of actions each actor will be able to program.
        Right now, this is dictated by the undead actors, and is the max among those undead
        actors."""
        return max([actor.round_actions for actor in self.actors.values() if actor.type == self._UNDEAD])

    def play_round_actions(self):
        """ I'm having a lot of trouble with this one. The problem is that after the
        actions are chosen, a direction needs to be chosen.  However, this means
        we can't just play out the whole round without getting more input from the player."""
        pass

    @property
    def current_actor(self):
        return self.actors[self.current_actor_num]

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
        # if not self.all_round_actions_collected:
        return self.current_actor.get_available_actions(self.actions_required_this_round)
        # else:
            # return self.current_player.get_available_directions(self.battle_grid)

    def _play_monster_action(self):
        self.current_actor.play_action(self.battle_grid, self.actors)
        self.current_actor_num = (self.current_actor_num + 1) % len(self.actors)

    def update_game_with_action(self, action: DungeonCrawlerAction) -> None:
        # if not self.all_round_actions_collected:
        self.round_actions.append(action)
        self.parse_action(action)
        self.current_actor_num = (self.current_actor_num + 1) % len(self.actors)
            # return
        # Something about this feels wrong.
        # I think the right move is to pass the action to the player, and let the player
        # decide what to do with it.

    def parse_action(self, action: DungeonCrawlerAction) -> None:
        if action.type == "move":
            self.current_actor.move(action)
        elif action.type == "attack":
            self.current_actor.attack(action, self.actors)
        elif action.type =="defend":
            self.current_actor.defend(action)
        elif action.type == "recover":
            self.current_actor.recover(action)

    def is_game_over(self) -> bool:
        if all([player.is_dead for player in self.human_players.values()]):
            for player in self.human_players.values():
                player.score = -1
            return True
        elif all([monster.is_dead for monster in self.monsters.values()]):
            for player in self.human_players.values():
                player.score = 1
            return True
        return False

    def start_round(self):
        pass

    def draw_board(self) -> None:
        pass

    def save_game_state(self) -> None:
        pass

    def load_save_game_state(self, dict) -> None:
        pass
