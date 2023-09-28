from .tile_container import MASTER_TILE_CONTAINER, TileContainer
from typing import ClassVar
from .action import AzulAction
from itertools import combinations
from .player_board import PlayerBoard
from games.game_components.player import Player as BasePlayer


class AzulPlayer(BasePlayer):
    model_config = {"arbitrary_types_allowed": True}
    max_tile_reserve: ClassVar[int] = 4
    done_placing: bool = False
    player_score: int = 5
    bonus_owed: int = 0
    player_board: PlayerBoard = PlayerBoard()
    player_tile_supply: TileContainer = MASTER_TILE_CONTAINER.copy()

    def _get_reserve_actions(self) -> list[AzulAction]:
        """Gets the reserve actions available to a player.
        This is an annoying one in that all combinations of player tiles are legal.
        For the sake of running a bot, we could assume this can't be called until
        the player has at most the max_tile_reserve number of tiles.
        Returns:
            list[AzulAction]: List of reserve actions
        """
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
        # I worry this will be dreadfully slow
        # There should be a more efficient way.
        for combination in combinations_list:
            action = AzulAction()
            for color in combination:
                action[AzulAction.BONUS_START + color] += 1
            actions.append(action)
        return actions

    def _get_placement_actions(self, wild_color: int) -> list[AzulAction]:
        """Gets the placement actions available to a player, given the
        current wild color and the player's tile supply.

        Args:
            wild_color (int): Current wild color for the round

        Returns:
            list[AzulAction]: list of placement actions
        """
        return self.player_board.get_tile_placement_actions(
            self.player_tile_supply, wild_color
        )

    def get_available_actions(self, wild_color: int):
        """Gets actions available to the player in phase 2.
        Note that in phase 1, actions available to a player do not
        depend on player attributes, so they are handled by the game.

        Also note that since bonus tiles are taken from the supply,
        and since they only knowing the player's required bonus,
        taking bonus tiles is handled by the game.

        Args:
            wild_color (int): _description_

        Returns:
            _type_: _description_
        """
        actions = []
        actions.append(self._get_placement_actions(wild_color))
        actions.append(self._get_reserve_actions())
        return actions

    def start_round_for_player(self):
        """Starts player round.  This resets the player's board
        """
        self.done_placing = False
        self.first_player = False
        self.player_tile_supply = self.player_board.reserved_tiles.remove_all_tiles()

    def _score_points_for_tile_placement(self, star: int, position: int):
        """Scores tiles for placement on a star.  This includes
        the points for the position, points for star completion (if any),
        and points for multistar bonus (if any).

        Args:
            star (int): Star tile was placed on
            position (int): Position tile was placed on
        """
        self.player_score += self.player_board.stars[
            star
        ].score_points_for_position_placed(position)
        self.player_score += self.player_board.check_multistar_bonus(position)

    def place_tile_on_star(self, action: AzulAction, wild_color: int) -> TileContainer:
        """Places a tile on a star.  The action is assumed to have the
        appropriate information for the placement.  This includes the star,
        position, and the number of wilds and non-wilds to spend.

        Args:
            action (AzulAction): Tile placing action, assumed to be valid
            wild_color (int): Wild color for the round

        Returns:
            TileContainer: When a tile is placed on a star, only one tile is
            physically placed on the board.  The rest are returned to the tower.
        """
        tile_color_to_place = action.tile_color_to_place(wild_color)
        if tile_color_to_place is None:
            tile_color_to_place = wild_color
            wilds_to_spend = 0
            color_tiles_to_spend = action.wilds_to_spend(wild_color)
        else:
            wilds_to_spend = action.wilds_to_spend(wild_color)
            color_tiles_to_spend = action.non_wilds_to_spend(wild_color)

        self.player_board.add_tile_to_star(
            action.star_to_place_tile,
            tile_color_to_place,
            action.position_to_place_tile,
        )
        tiles_spent = TileContainer(
            {tile_color_to_place: color_tiles_to_spend, wild_color: wilds_to_spend}
        )
        self.player_tile_supply.subtract(tiles_spent)

        self._score_points_for_tile_placement(
            action.star_to_place_tile, action.position_to_place_tile
        )
        self.bonus_owed += self.player_board.bonus_tile_lookup(
            action.star_to_place_tile, action.position_to_place_tile
        )
        return_to_tower = tiles_spent.subtract({color_tiles_to_spend: 1})
        return return_to_tower

    def add_tiles_to_player_supply(self, tiles: TileContainer):
        self.player_tile_supply += tiles

    def reserve_tiles(self, action: AzulAction):
        """Moves tiles from the player's supply to the player's reserve.
        This completes the round for the player.
        The count of non-reserved tiles are subtracted from the player's score
        and the tiles themselves are returned to the tower.

        Args:
            action (AzulAction): Action, assumed to be valid.
        """
        tiles_to_reserve = TileContainer(action.tiles_to_reserve)
        self.player_board.reserved_tiles += self.player_tile_supply.subtract(
            tiles_to_reserve
        )
        self.player_score -= self.player_tile_supply.total()
        self.player_score = max(self.player_score, 0)
        self.done_placing = True
        return self.player_tile_supply.remove_all_tiles()

