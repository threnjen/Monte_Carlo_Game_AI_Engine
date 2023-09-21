# %%
from __future__ import annotations
from random import randrange
from games.azul.factory import Factory
from games.azul.tile_container import Supply, Bag, MASTER_TILE_CONTAINER, TileContainer
from games.azul.player import Player
from pydantic import BaseModel, Field
from typing import ClassVar


class Game(BaseModel):
    """The game class will handle all aspects of the game.  All other objects will
    be instantiated in here.
    """
    model_config = {'arbitrary_types_allowed': True}
    tiles_per_factory: ClassVar[int] = 4
    tiles_per_color: ClassVar[int] = 22
    total_rounds: ClassVar[int] = 6
    supply_max: ClassVar[int] = 10
    reserve_max: ClassVar[int] = 4
    wild_list: ClassVar[dict[int, str]] = {
        1: "purple",
        2: "green",
        3: "orange",
        4: "yellow",
        5: "blue",
        6: "red",
    }
    # Number of factory displays by player count
    factory_display_requirement: ClassVar[dict[int, int]] = {1: 9, 2: 5, 3: 7, 4: 9}
    cost_to_take_first_player: ClassVar[int] = -2
    player_count: int
    current_round: int = 1
    current_player_num: int = None
    first_player: int = None
    wild_color: str = None
    name: str = "Azul"
    phase: int = 1
    game_over: bool = False
    factory: Factory = None
    supply: Supply = Supply()
    players: dict[int, Player] = None
    bag: Bag = Field(
        default_factory=lambda: Bag(
            {color: Game.tiles_per_color for color in MASTER_TILE_CONTAINER.keys()}
        )
    )
    tower: TileContainer = MASTER_TILE_CONTAINER.copy()
    
    def model_post_init(self, __context) -> None:
        if self.factory is None:
            self.factory = Factory(display_count=Game.factory_display_requirement[self.player_count])
        if self.players is None:
            self.players = {
                i: Player(player_number=i, first_player=False)
                for i in range(self.player_count)
            }
        if self.first_player is None:
            self.first_player = randrange(0, self.player_count)
        self.players[self.first_player].first_player = True
        self.start_round()

    def fill_supply(self):
        """Fills the supply with tiles (up to 10).  Called at the beginning
        of the game, beginning of the round, and after a player is done placing tiles
        in phase two."""

        supply_count = self.supply.total()
        self.supply.fill_supply(
            self.bag.randomly_choose_tiles(Game.supply_max - supply_count, self.tower)
        )

    def move_reserves_to_player_supply(self):
        for player in self.players.values():
            player.player_tile_supply += (
                player.player_board.reserved_tiles.remove_all_tiles()
            )

    def set_new_wild_color(self):
        self.wild_color = Game.wild_list[self.current_round]

    def fill_all_factory_displays(self):
        for display in self.factory.factory_displays.values():
            display += self.bag.randomly_choose_tiles(
                Game.tiles_per_factory, self.tower
            )

    def set_game_phase(self, phase: int):
        self.phase = phase

    def set_current_player(self, player: int):
        self.current_player_num = player

    def reset_players_for_round(self):
        for player in self.players.values():
            player.done_placing = False

    def start_round(self):
        """Begins a round (including the first one).

        Args:
            round (int): Round number
            wild_color (str): Wild color for the round.
        """
        self.fill_supply()
        self.set_new_wild_color()
        self.fill_all_factory_displays()
        self.move_reserves_to_player_supply()
        self.set_game_phase(1)
        self.set_current_player(self.first_player)
        self.reset_players_for_round()
        self.factory.center.reset_first_player()

    def is_game_over(self) -> bool:
        return self.game_over

    def get_game_scores(self) -> dict[int, int]:
        return {
            player_num: player.player_score
            for player_num, player in self.players.items()
        }

    def play_game(self):
        """Plays the game (in the case where we are not using a bot)"""
        while not self.is_game_over():
            pass
            # This is the hard part.
            # Roughly speaking:
            # Players take turns
            # Resolve the board consequences
            # end round if needed




# %%
test = Game(player_count=2)
import json
with open("test.json", "w") as f:
    f.write(json.dumps(test.model_dump()))

