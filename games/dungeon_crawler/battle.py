from games.game_components.base_game_object import BaseGameObject
from .battle_grid import BattleGrid
from pydantic import field_validator, Field
from .action import DungeonCrawlerAction
from .actor import Actor
from .player import Player
from .enemy import Enemy


class Battle(BaseGameObject):
    model_config = {"arbitrary_types_allowed": True}
    actors: dict[str, Actor]
    current_actor_num: int = 0
    save_game: dict = None
    battle_grid: BattleGrid = Field(default_factory=BattleGrid, validate_default=True)
    round_actions: list[tuple[int, DungeonCrawlerAction]] = None
    human_players: dict = None
    monsters: dict = None
    round_num: int = 0

    @field_validator("battle_grid")
    @classmethod
    def create_battle_grid(cls, battle_grid):
        if battle_grid is None:
            battle_grid = BattleGrid()


    def model_post_init(self):
        if self.human_players is None:
            self.human_players = {
                name: actor
                for name, actor in self.actors.items()
                if isinstance(actor, Player)
            }

        if self.monsters is None:
            self.monsters = {
                name: actor
                for name, actor in self.actors.items()
                if isinstance(actor, Enemy)
            }

    @field_validator("round_num", mode="before")
    @classmethod
    def create_round_num(cls, round_num):
        if round_num == 0:
            round_num = 1

    @property
    def human_player_count(self):
        return len(
            [actor for actor in self.actors.values() if isinstance(actor, Player)]
        )

    def set_round_order(self):
        self.actors = dict(
            sorted(self.actors.items(), key=lambda x: x[1].actor_initiative)
        )

    @property
    def actions_required_this_round(self) -> int:
        """The game needs to know the number of actions each actor will be able to program.
        Right now, this is dictated by the undead actors, and is the max among those undead
        actors."""
        return max([actor.required_action_count for actor in self.actors.values() if isinstance(actor, Enemy)])

    def play_round_actions(self):
        for actor in self.actors:
            if actor.is_dead:
                continue
            if isinstance(actor, Player):
                self.parse_action(actor.round_stack.pop())
            elif isinstance(actor, Enemy):
                self._play_monster_action()

    @property
    def current_actor(self):
        return self.actors[self.current_actor_num]

    @property
    def all_round_actions_collected(self) -> bool:
        """A boolean to determine if all players have programmed their actions for the round."""
        return len(self.round_actions) == self.actions_required_this_round * len(
            self.human_player_count
        )

    def get_available_actions(
        self, special_policy: bool = False
    ) -> list[DungeonCrawlerAction]:
        """This is the function that the game will call to get the available actions for the current player.
        There are two possibilities:
            - The player is programming their actions for the round.  In this case, the player will be able to
            choose from a list of card permutations.
            - The player is choosing a direction to enact their chosen action.  They need the battle grid to
            determine adjacent empty and occupied squares."""
        # if not self.all_round_actions_collected:
        return self.current_actor.get_available_actions(
            self.actions_required_this_round
        )
        # else:
        # return self.current_player.get_available_directions(self.battle_grid)

    def _play_monster_action(self):
        self.current_actor.play_action(self.battle_grid, self.actors)
        self.current_actor_num = (self.current_actor_num + 1) % len(self.actors)

    def update_game_with_action(self, action: DungeonCrawlerAction) -> None:
        # if not self.all_round_actions_collected:
        self.round_actions.append(action)
        if self.all_round_actions_collected:
            self.play_round_actions()
        self.current_actor_num = (self.current_actor_num + 1) % len(self.actors)
        # return
        # Something about this feels wrong.
        # I think the right move is to pass the action to the player, and let the player
        # decide what to do with it.

    def parse_action(self, action: DungeonCrawlerAction) -> None:
        if action.type == "move":
            self.current_actor.move(action, self.actors, self.battle_grid)
        elif action.type == "attack":
            self.current_actor.attack(action, self.actors)
        elif action.type == "defend":
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
        for actor in self.actors.values():
            actor.begin_new_round()

    def draw_board(self) -> None:
        pass

    def save_game_state(self) -> None:
        pass

    def load_save_game_state(self, dict) -> None:
        pass
