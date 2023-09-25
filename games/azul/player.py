from .tile_container import MASTER_TILE_CONTAINER, TileContainer
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

    def reserve_tiles(self, tiles_to_reserve: TileContainer):
        self.player_tile_supply.subtract(tiles_to_reserve)

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

    def get_available_actions(self, game: AzulGame):
        actions = []
        if game.phase == 1:
            actions.append(game.get_available_actions())
        elif game.phase == 2:
            if self.bonus_owed > 0:
                actions.append(game.supply.get_available_actions(self.bonus_owed))
            else:
                actions.append(self._get_placement_actions(game.wild_color))
                actions.append(self._get_reserve_actions())
        return actions

    def _score_points_for_tile_placement(self, star: int, position: int):
        self.player_score += self.player_board.stars[star].score_points_for_position_placed(position)
        self.player_score += self.player_board.check_multistar_bonus(position)

    def _update_placement_action(self, action: AzulAction, game: AzulGame):
        if sum(action[AzulAction.STAR_START: AzulAction.STAR_END]) == 1:
            star = np.argmax(action[AzulAction.STAR_START: AzulAction.STAR_END])
            position = np.argmax(action[AzulAction.STAR_POINT_START: AzulAction.STAR_POINT_END])
            leftover_tiles = self.player_board.update_game_with_action(action, game.wild_color)
            self._score_points_for_tile_placement(star, position)
            self.bonus_owed += self.player_board.bonus_tile_lookup(star, position)
            game.tower += leftover_tiles

    def _update_reserve_action(self, action: AzulAction):
        if sum(action[AzulAction.RESERVE_TILE_START: AzulAction.RESERVE_TILE_END]) > 0:
            tiles_to_reserve = TileContainer({color: action[AzulAction.RESERVE_TILE_START + color] for color in MASTER_TILE_CONTAINER.keys()})
            self.reserve_tiles(tiles_to_reserve)
            self.done_placing = True

    def _update_take_bonus_action(self, action: AzulAction, game: AzulGame):
        if sum(action[AzulAction.BONUS_START: AzulAction.BONUS_END]) > 0:
            selected_bonus = TileContainer({color: action[AzulAction.BONUS_START + color] for color in MASTER_TILE_CONTAINER.keys()})
            self.player_tile_supply += game.supply.subtract(selected_bonus)
            self.bonus_owed = 0

    def update_game_with_action(self, action: AzulAction, game: AzulGame):
        self._update_placement_action(action, game)
        self._update_placement_action(action, game)
        self._update_reserve_action(action)

    def _get_placement_actions(self, wild_color: int) -> list[AzulAction]:
        return self.player_board.get_available_actions(self.player_tile_supply, wild_color)

    def start_round_for_player(self):
        self.done_placing = False
        self.first_player = False
        self.player_tile_supply = self.player_board.reserved_tiles.remove_all_tiles()