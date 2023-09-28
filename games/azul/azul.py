# %%
from __future__ import annotations
from .factory import Factory
from .tile_container import (
    Supply,
    Bag,
    MASTER_TILE_CONTAINER,
    TileContainer,
    RED,
    BLUE,
    YELLOW,
    GREEN,
    ORANGE,
    PURPLE,
)
from .action import AzulAction
from pydantic import BaseModel, Field
from typing import ClassVar
from .player import AzulPlayer
from random import choice


class AzulGame(BaseModel):
    """The game class will hold all game objects that are not owned by a player.
    This includes the factory displays, the supply, the bag, the tower, and the
    center display.  It will also holds some of the game metadata.
    """

    model_config = {"arbitrary_types_allowed": True}

    player_count: int
    # Players are index by integers starting at 0
    players: dict[int, AzulPlayer] = None
    # wild_color is the color that is wild for the round.  It is set at the beginning of the round.
    # Note that colors are represented by integers starting at 0
    # This is to make it easier to use as an index for numpy arrays.
    wild_color: int = None
    name: str = "Azul"
    phase: int = 1
    # The current round starts at zero and then increments to one when
    # the game begins.
    # This is because it is easier to increment the round at the beginning of the round,
    # and when the game is instantiated the round is not yet begun.
    current_round: int = 0
    game_over: bool = False
    factory: Factory = None
    first_player_num: int = None
    current_player_num: int = 0
    training: bool = False

    tiles_per_factory: ClassVar[int] = 4
    tiles_per_color: ClassVar[int] = 22
    total_rounds: ClassVar[int] = 6
    supply_max: ClassVar[int] = 12
    reserve_max: ClassVar[int] = 4
    # Wild list by round.  Rounds are indexed starting at 1.
    wild_list: ClassVar[dict[int, int]] = {
        1: PURPLE,
        2: GREEN,
        3: ORANGE,
        4: YELLOW,
        5: BLUE,
        6: RED,
    }
    # Number of factory displays by player count
    factory_display_requirement: ClassVar[dict[int, int]] = {1: 9, 2: 5, 3: 7, 4: 9}
    cost_to_take_first_player: ClassVar[int] = 2

    supply: Supply = Supply()
    # We can instantiate the bag with the correct number of tiles per color
    # because it doesn't depend on any object attributes, just class attributes.
    bag: Bag = Field(
        default_factory=lambda: Bag(
            {color: AzulGame.tiles_per_color for color in MASTER_TILE_CONTAINER.keys()}
        )
    )
    tower: TileContainer = TileContainer(MASTER_TILE_CONTAINER.copy())

    @property
    def current_player(self) -> AzulPlayer:
        return self.players[self.current_player_num]

    def model_post_init(self, __context) -> None:
        """Initializes the game objects.  This is called after the model is initialized.
        If we're loading a pre-existing game state, this does nothing."""
        # Create factory displays based on player count
        if self.factory is None:
            self.factory = Factory(
                display_count=AzulGame.factory_display_requirement[self.player_count]
            )
        # Creates desired number of players
        if self.players is None:
            self.players = {
                player_num: AzulPlayer(player_number=player_num)
                for player_num in range(self.player_count)
            }
        # Sets the first player
        if self.first_player_num is None:
            self.first_player_num = choice(list(self.players.keys()))

    def draw_board(self):
        # Not implemented yet.
        pass

    def get_available_actions(self, special_policy: bool = False) -> list[AzulAction]:
        """Actions available to the current player.
        This will depend on the phase of the game (tile taking or tile placement)

        Args:
            special_policy (bool, optional):  Not used. Defaults to False.

        Returns:
            list[AzulAction]: List of numpy arrays representing actions.
        """
        if self.phase == 1:
            actions = self.factory.get_available_actions()
        if self.phase == 2:
            if self.current_player.bonus_owed > 0:
                actions = self.supply.get_available_actions(self.current_player.bonus_owed)
            else:
                actions = self.current_player.get_available_actions(self.wild_color)
        return actions

    def _play_phase_one_action(self, action: AzulAction):
        """Plays a phase one action.  This includes taking tiles from a factory display
        and placing it the player supply.  If the displays are all empty, we move
        to phase two for the round.  Otherwise, we move to the next player.

        Args:
            action (AzulAction): Requires a valid action for the phase and the board.
        """
        new_tiles, first_player_ind = self.factory.take_tiles(action, self.wild_color)
        if first_player_ind:
            self.first_player_num = self.current_player_num
        self.current_player.add_tiles_to_player_supply(new_tiles)
        if self.factory.is_factory_empty():
            self.current_player_num = self.first_player_num
            self._set_game_phase(2)
        else:
            self.current_player_num = (self.current_player_num + 1) % self.player_count

    def _play_phase_two_action(self, action: AzulAction):
        """Plays a phase two action.  This includes placing tiles on the player board,
        taking bonus tiles, and reserving tiles.  If all players are done placing,
        we move to the next round.  Otherwise, we move to the next player when the current
        player has finished placing tiles.

        Args:
            action (AzulAction): Requires a valid action for the phase, player board, and supply.
        """
        if action.tile_placement_action_ind:
            leftover_tiles = self.current_player.place_tile_on_star(action, self.wild_color)
            self.tower += leftover_tiles
        if action.take_bonus_tiles_ind:
            selected_bonus = self.supply.take_tile(action)
            self.current_player.add_tiles_to_player_supply(selected_bonus)
            self.current_player.bonus_owed = 0
        if action.reserve_tile_action_ind:
            leftover_tiles = self.current_player.reserve_tiles(action)
            self.tower += leftover_tiles
            self._fill_supply()
            self.current_player_num = (self.current_player_num + 1) % self.player_count
        if all([player.done_placing for player in self.players.values()]):
            self.current_player_num = self.first_player_num
            self.start_round()

    def update_game_with_action(self, action: AzulAction, player: int):
        """Plays the action.  The action is assumed to be valid.
        Note the player number is not necessary, since to be valid
        the action must be available to the current player."""
        if self.phase == 1:
            self._play_phase_one_action(action)
        elif self.phase == 2:
            self._play_phase_two_action(action)

    def _fill_supply(self):
        """Fills the supply with tiles (up to 10).  Called at the beginning
        of the game, beginning of the round, and after a player is done placing tiles
        in phase two."""

        supply_count = self.supply.total()
        self.supply.fill_supply(
            self.bag.randomly_choose_tiles(
                AzulGame.supply_max - supply_count, self.tower
            )
        )

    def _set_new_wild_color(self):
        self.wild_color = AzulGame.wild_list[self.current_round]

    def _fill_all_factory_displays(self):
        for display in self.factory.factory_displays.values():
            display += self.bag.randomly_choose_tiles(
                AzulGame.tiles_per_factory, self.tower
            )

    def _set_game_phase(self, phase: int):
        self.phase = phase

    def _increment_round(self):
        self.current_round += 1

    def start_round(self):
        """Begins a round (including the first one).

        Args:
            round (int): Round number
            wild_color (int): Wild color for the round.
        """
        self._increment_round()
        if self.current_round > AzulGame.total_rounds:
            self.game_over = True
            return
        self._fill_supply()
        self._set_new_wild_color()
        self._fill_all_factory_displays()
        self._set_game_phase(1)
        for player in self.players.values():
            player.start_round_for_player()

    def is_game_over(self) -> bool:
        return self.game_over
