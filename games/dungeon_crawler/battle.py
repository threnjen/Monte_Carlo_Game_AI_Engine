from games.game_components.base_game_object import BaseGameObject
from .battle_grid import BattleGrid
from pydantic import field_validator, Field
from .action import DungeonCrawlerAction
from .actor import Actor
from .player import Player
from .enemy import Enemy

# TODO  It really feels like there's too much going on in this file.  We may need to break it up.


class Battle(BaseGameObject):
    model_config = {"arbitrary_types_allowed": True}
    actors: dict[str, Actor]
    current_actor_num: int = 0
    save_game: dict = None
    battle_grid: BattleGrid = Field(default_factory=BattleGrid, validate_default=True)
    round_actions: list[tuple[int, DungeonCrawlerAction]] = None
    human_players: dict[str, Actor] = None
    monsters: dict[str, Actor] = None
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
        if self.round_num == 1:
            self.start_round()

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
        return max(
            [
                actor.required_action_count
                for actor in self.actors.values()
                if isinstance(actor, Enemy)
            ]
        )

    def play_round_actions(self):
        """Something about this feels REALLY clunky."""
        for _ in enumerate(self.actions_required_this_round):
            for actor in self.actors.values():
                if actor.is_dead:
                    continue
                self.current_actor.play_action(self.actors, self.battle_grid)
                self.set_next_actor()
        self.start_round()

    @property
    def current_actor(self) -> Actor:
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
        return self.current_actor.get_available_actions(
            self.actions_required_this_round
        )

    def set_next_actor(self):
        self.current_actor_num = (self.current_actor_num + 1) % len(self.actors)

    def update_game_with_action(self, action: DungeonCrawlerAction) -> None:
        self.round_actions.append(action)
        if not self.all_round_actions_collected:
            while self.current_actor.is_dead or isinstance(self.current_actor, Enemy):
                self.set_next_actor()
            return
        if self.all_round_actions_collected:
            self.play_round_actions()
        self.current_actor_num = (self.current_actor_num + 1) % len(self.actors)

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
        self.round_num += 1
        for actor in self.actors.values():
            actor.begin_new_round()

    def draw_board(self) -> None:
        pass

    def save_game_state(self) -> None:
        pass

    def load_save_game_state(self, dict) -> None:
        pass


if __name__ == "__main__":
    battle = Battle(
        actors={
            "player1": Player(location_on_grid=(1, 1)),
            "monster1": Enemy(location_on_grid=(3, 4)),
        },
    )
