from .tile_container import MASTER_TILE_CONTAINER, TileContainer
from .factory import Factory
from typing import ClassVar
from .action import AzulAction
from itertools import combinations
from .player_board import PlayerBoard
from games.game_components.player import Player as BasePlayer
from .azul import AzulGame
import numpy as np

class AzulPlayer(BasePlayer):
    model_config = {"arbitrary_types_allowed": True}
    max_tile_reserve: ClassVar[int] = 4
    done_placing: bool = False
    player_score: int = 5
    bonus_owed: int = 0
    player_board: PlayerBoard = PlayerBoard()
    player_tile_supply: TileContainer = MASTER_TILE_CONTAINER.copy()

    def _get_reserve_actions(self) -> list[AzulAction]:
        if self.max_tile_reserve >= self.player_tile_supply.total():
            action = AzulAction()
            for color in self.player_tile_supply():
                action[AzulAction.BONUS_START + color] = self[color]
            return [action]
        combinations_list = list(
            combinations(
                list(self.player_tile_supply.elements()), self.max_tile_reserve()
            )
        )
        actions = []
        for combination in combinations_list:
            action = AzulAction()
            for color in combination:
                action[AzulAction.BONUS_START + color] += 1
            actions.append(action)
        return actions
    
    def _get_placement_actions(self, wild_color: int) -> list[AzulAction]:
        return self.player_board.get_available_actions(self.player_tile_supply, wild_color)

    def get_available_actions(self, wild_color: int):
        actions = []
        actions.append(self._get_placement_actions(wild_color))
        actions.append(self._get_reserve_actions())
        return actions

    def start_round_for_player(self):
        self.done_placing = False
        self.first_player = False
        self.player_tile_supply = self.player_board.reserved_tiles.remove_all_tiles()

    def _score_points_for_tile_placement(self, star: int, position: int):
        self.player_score += self.player_board.stars[star].score_points_for_position_placed(position)
        self.player_score += self.player_board.check_multistar_bonus(position)

    def place_tile_action(self, action: AzulAction, wild_color: int):
        # This action is broken
        # Things to do
        # Determine tile color to add
        # Add tile to star (done)
        # Subtract tiles from player supply
        # Place tiles back in the tower
        self.player_board.add_tile_to_star(action.star_to_place_tile)
        leftover_tiles = self.player_board.update_game_with_action(action, wild_color)
        self._score_points_for_tile_placement(action.star_to_place_tile, action.position_to_place_tile)
        self.bonus_owed += self.player_board.bonus_tile_lookup(action.star_to_place_tile, action.position_to_place_tile)
        return leftover_tiles

    def add_tiles_to_player_supply(self, tiles: TileContainer):
        self.player_tile_supply += tiles

    def reserve_tiles(self, tiles_to_reserve: TileContainer):
        self.player_board.reserved_tiles += self.player_tile_supply.subtract(tiles_to_reserve)
        self.player_score -= self.player_tile_supply.total()
        self.player_tile_supply.clear()
        self.done_placing = True
