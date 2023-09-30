from pydantic import BaseModel, Field
from typing import ClassVar, Any
from .tile_container import TileContainer, MASTER_TILE_CONTAINER, RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE
from .action import AzulAction
import numpy as np

ALL = PURPLE + 1

class Star(BaseModel):
    """Player board star.  There are seven possible:  six colors and one colorless,
    denoted here as 'all'.  The primary action here is to add a tile, and the primary
    return is the points received.

    Args:
        object (object): Star on player board.
    """

    STAR_POINTS: ClassVar[dict[int, int]] = {
        RED: 14,
        GREEN: 18,
        ORANGE: 17,
        YELLOW: 16,
        BLUE: 15,
        PURPLE: 20,
        ALL: 12,
    }
    STAR_SIZE: ClassVar[int] = 6
    color: int
    star_full: bool = False
    star_full_points_received: bool = False
    filled_positions: dict[int, bool] = Field(
        default_factory=lambda: {i: False for i in range(1, Star.STAR_SIZE + 1)}
    )
    colors_allowed: dict[int, bool] = {
        color: False for color in MASTER_TILE_CONTAINER.keys()
    }

    def model_post_init(self, __context: Any) -> None:
        """If the start type is all, we need to allow all colors initially.
        Afterward, we will restrict as tiles are placed.
        Otherwise, we will restrict to the single color of the star.  This seem
        redundant, but is to avoid different treatment for the ALL start later.
        """
        if self.color == ALL:
            self.colors_allowed = {color: True for color in self.colors_allowed.keys()}
        else:
            self.colors_allowed[self.color] = True

    def place_tiles_on_star(self, position: int, color: int):
        """Adds a tile to the board at a given position.
        This can only be done if the position is empty and if the
        player has the required tiles.  However, the tile requirement
        check is done elsewhere.

        Args:
            position (int): Position to place tile
            color (int): Tile color placed.

        Returns:
            int: Points gained from tile placement, including completing the star if applicable.
        """

        self.filled_positions[position] = True
        if self.color == ALL:
            self.colors_allowed[color] = False
        if all([value for value in self.filled_positions.values()]):
            self.star_full = True

    def score_points_for_position_placed(self, position: int) -> int:
        """Scores points for a given position, if it is filled.  This is used
        for the end of the round.

        Position points come from adjacent tiles, and are calculated by
        checking the number of contiguous tiles to the left and right.  Note
        that this is not the same as the number of tiles in the star, since not
        all tiles placed may be contiguous.

        Args:
            position (int): Position to score

        Returns:
            int: Points earned
        """
        points = self.check_contiguous(position)
        if not self.star_full_points_received and self.star_full:
            points += Star.STAR_POINTS[self.color]
            self.star_full_points_received = True
        return points

    def get_available_actions(self, tiles: TileContainer, wild_color: int):
        """Lists all possible actions for the star.  This checks the available colors for the star
        and the available tiles for the player (passed as the tiles parameter).  A player can only
        place a tile if they have the required tiles, and they can only place a tile if the color
        is allowed for the star.

        Args:
            tiles (TileContainer): Tiles available to place
            wild_color (int): Wild color for the round

        Returns:
            list: List of potential actions
        """
        actions = []
        # This is only a nontrivial loop for the center "all" star
        for color in self.colors_allowed.keys():
            if not self.colors_allowed[color]:
                continue
            for position in self.filled_positions.keys():
                if self.filled_positions[position]:
                    continue
                actions.append(
                    self._generate_actions_for_position(
                        tiles, position, color, wild_color
                    )
                )
        return actions

    def _generate_actions_for_position(
        self, tiles: TileContainer, position: int, color: int, wild_color: int
    ) -> list[AzulAction]:
        """Checks the actions available for a star position.  This is a helper function for
        get_available_actions.  It checks the number of tiles available for the color and
        the number of wilds available.  It then generates all possible combinations of tiles
        and wilds that can be placed in the position.  Note that this is a list of actions,
        since there may be multiple ways to place tiles.

        To place tiles, a player must have at least one tile for the color they're trying to
        place.

        Args:
            tiles (TileContainer): Tiles available to place
            position (int): Position on the start to place tiles
            color (int): Color of tiles to place.  This needn't match the star color (in case of
            the "all" star)
            wild_color (int): Wild color for the round

        Returns:
            list[AzulAction]: List of actions available for the position
        """
        # If we're playing a wild, there's only one way to fill a position with just wilds
        if color == wild_color:
            action = AzulAction()
            action[AzulAction.STAR_POINT_START + position] = 1
            action[AzulAction.STAR_SPEND_COLOR_START + color] = position
            return [action]
        # Otherwise, we need to generate all possible combinations of wilds and the color
        action_list = []
        # We demand at least one non-wild tile, and we must have sufficient primary color tiles
        # This means our primary tile count has a range of possible
        # spending amounts.  On the low end, it must be at least 1,
        # But also is required to be large enough so that the primary count + the wild count is
        # at least as large as the position.
        # On the higher end of the range, we can't spend more primary tiles than we have, and can
        # only spend as many as the position.
        for primary_color_count in range(
            max(position - tiles.get(wild_color, 0), 1),
            min(tiles.get(color, 0), position) + 1,
        ):
            if primary_color_count > tiles.get(color, 0):
                continue
            action = AzulAction()
            action[AzulAction.STAR_POINT_START + position] = 1
            action[AzulAction.STAR_SPEND_COLOR_START + color] = primary_color_count
            action[AzulAction.STAR_SPEND_COLOR_START + wild_color] = (
                position - primary_color_count
            )
            action_list.append(action)
        return action_list

    def check_left_contiguous(self, position: int) -> int:
        """Checks the number of contiguous tiles to the left and returns the point value,
        as though those were the only tiles.  We'll do right contiguous later.

        Args:
            position (int): Position of tile being placed.

        Returns:
            int: Points received (so far)
        """
        points = 1
        # We get one point for the tile we just placed, and then check
        # the tiles to the left.  For each tile we find, we get one point.
        # If we find an empty tile, we stop.
        for points in range(1, self.STAR_SIZE + 1):
            if self.filled_positions[(position - points - 1) % self.STAR_SIZE + 1]:
                pass
            else:
                return points
        return self.STAR_SIZE

    def check_right_contiguous(self, position: int, points: int) -> int:
        """Checks the number of right contiguous tiles and returns the point value, in addition
        to the left-contiguous tiles.

        Args:
            position (int): Position of tile placed.
            points (int): Points

        Returns:
            int: Points
        """
        distance = 1
        # We check the tiles to the right.  For each tile we find, we get one point and add it
        # to the points we received.  If we find an empty tile, we stop and return the total
        # Otherwise, we return the max points (equal to the star size)
        for distance in range(1, self.STAR_SIZE):
            if self.filled_positions[(position + distance - 1) % self.STAR_SIZE + 1]:
                points += 1
            else:
                return points
        return self.STAR_SIZE

    def check_contiguous(self, position: int) -> int:
        """Checks both left and right contiguous from a given position.
        This is used to determine points when placing a tile. Right contiguous
        is only needed to be checked if left contiguous returns points
        less than the star size.

        Args:
            position (int): position to check

        Returns:
            int: Points earned
        """
        points = self.check_left_contiguous(position)
        if points < self.STAR_SIZE:
            points = self.check_right_contiguous(position, points)
        return points


class PlayerBoard(BaseModel):
    """The player board stores the player stars, which in turn store the tiles placed.
    It may be best to have a function to add tiles to the star from here."""

    model_config = {"arbitrary_types_allowed": True}

    BONUS_STAR_INDEX: ClassVar[int] = 0
    BONUS_POS_INDEX: ClassVar[int] = 1
    FILL_ALL_POS_BONUS: ClassVar[int] = 4
    TILE_PREFIX: ClassVar[str] = "star"
    reserved_tiles: TileContainer = TileContainer(MASTER_TILE_CONTAINER.copy())
    stars: dict[int, Star] = {
        color: Star(color=color)
        for color in list(MASTER_TILE_CONTAINER.keys()) + [ALL]
    }
    BONUSES_LOOKUP: ClassVar[dict[str, list[str]]] = {
        "blue1": ["YBS"],
        "blue2": ["YBS", "BAP"],
        "blue3": ["BAP", "BRS"],
        "blue4": ["BRS"],
        "blue5": ["BW"],
        "blue6": ["BW"],
        "red1": ["BRS"],
        "red2": ["BRS", "RAP"],
        "red3": ["RAP", "ROS"],
        "red4": ["ROS"],
        "red5": ["RW"],
        "red6": ["RW"],
        "orange1": ["ROS"],
        "orange2": ["ROS", "OAP"],
        "orange3": ["OAP", "OPS"],
        "orange4": ["OPS"],
        "orange5": ["OW"],
        "orange6": ["OW"],
        "purple1": ["OPS"],
        "purple2": ["OPS", "PAP"],
        "purple3": ["PAP", "PGS"],
        "purple4": ["PGS"],
        "purple5": ["PW"],
        "purple6": ["PW"],
        "green1": ["PGS"],
        "green2": ["PGS", "GAP"],
        "green3": ["GAP", "GYS"],
        "green4": ["GYS"],
        "green5": ["GW"],
        "green6": ["GW"],
        "yellow1": ["GYS"],
        "yellow2": ["GYS", "YAP"],
        "yellow3": ["YAP", "YBS"],
        "yellow4": ["YBS"],
        "yellow5": ["YW"],
        "yellow6": ["YW"],
        "all1": ["OAP", "RAP"],
        "all2": ["RAP", "BAP"],
        "all3": ["BAP", "YAP"],
        "all4": ["YAP", "GAP"],
        "all5": ["GAP", "PAP"],
        "all6": ["PAP", "OAP"],
    }

    BONUS_CRITERIA: ClassVar[dict[str, dict]] = {
        "BAP": {
            "criteria": [(BLUE, 2), (BLUE, 3), (ALL, 2), (ALL, 3)],
            "reward": 1,
        },
        "YAP": {
            "criteria": [(YELLOW, 2), (YELLOW, 3), (ALL, 2), (ALL, 3)],
            "reward": 1,
        },
        "GAP": {
            "criteria": [(GREEN, 2), (GREEN, 3), (ALL, 2), (ALL, 3)],
            "reward": 1,
        },
        "PAP": {
            "criteria": [(PURPLE, 2), (PURPLE, 3), (ALL, 2), (ALL, 3)],
            "reward": 1,
        },
        "OAP": {
            "criteria": [(ORANGE, 2), (ORANGE, 3), (ALL, 2), (ALL, 3)],
            "reward": 1,
        },
        "RAP": {
            "criteria": [(RED, 2), (RED, 3), (ALL, 2), (ALL, 3)],
            "reward": 1,
        },
        "OPS": {
            "criteria": [(ORANGE, 3), (ORANGE, 4), (PURPLE, 1), (PURPLE, 2)],
            "reward": 2,
        },
        "PGS": {
            "criteria": [(PURPLE, 3), (PURPLE, 4), (GREEN, 1), (GREEN, 2)],
            "reward": 2,
        },
        "GYS": {
            "criteria": [(GREEN, 3), (GREEN, 4), (YELLOW, 1), (YELLOW, 2)],
            "reward": 2,
        },
        "YBS": {
            "criteria": [(YELLOW, 3), (YELLOW, 4), (BLUE, 1), (BLUE, 2)],
            "reward": 2,
        },
        "BRS": {
            "criteria": [(BLUE, 3), (BLUE, 4), (RED, 1), (RED, 2)],
            "reward": 2,
        },
        "ROS": {
            "criteria": [(RED, 3), (RED, 4), (ORANGE, 1), (ORANGE, 2)],
            "reward": 2,
        },
        "OW": {"criteria": [(ORANGE, 5), (ORANGE, 6)], "reward": 3},
        "PW": {"criteria": [(PURPLE, 5), (PURPLE, 6)], "reward": 3},
        "GW": {"criteria": [(GREEN, 5), (GREEN, 6)], "reward": 3},
        "YW": {"criteria": [(YELLOW, 5), (YELLOW, 6)], "reward": 3},
        "BW": {"criteria": [(BLUE, 5), (BLUE, 6)], "reward": 3},
        "RW": {"criteria": [(RED, 5), (RED, 6)], "reward": 3},
    }

    def get_tile_placement_actions(self, tiles: TileContainer, wild_color: int) -> list[AzulAction]:
        """Gets all possible actions for placing tiles on the player board.  This is done by
        checking all stars and all positions on the stars, and then checking the available
        actions for each position.  Note that each position results in a list of actions,
        since there may be multiple ways to place tiles.

        Args:
            tiles (TileContainer): Tiles that could be available to be placed.
            wild_color (int): Wild color for the round, which influences tiles we can place.

        Returns:
            list[AzulAction]: possible actions for tile placing.
        """
        action_list = []
        for star in self.stars.values():
            if star.star_full:
                continue
            action_list.append(star.get_available_actions(tiles, wild_color))
        return action_list

    def add_tile_to_star(self, star_color: int, tile_color: int, position: int):
        self.stars[star_color].place_tiles_on_star(position, tile_color)

    def update_game_with_action(self, action: AzulAction, wild_color: int):
        """Updates the game with the action taken.  This includes updating the player
        board and returning the points earned.

        Args:
            action (AzulAction): Action taken
            wild_color (int): Wild color for the round

        Returns:
            int: Points earned
        """
        color = np.argmax(action[AzulAction.STAR_SPEND_COLOR_START: AzulAction.STAR_SPEND_COLOR_END])
        color_amount = max(action[AzulAction.STAR_SPEND_COLOR_START: AzulAction.STAR_SPEND_COLOR_END])
        if color != wild_color:
            wild_tiles = action[AzulAction.STAR_SPEND_COLOR_START + wild_color]
        else:
            wild_tiles = 0
        action[AzulAction.STAR_SPEND_COLOR_START + wild_color] = 0
        
        return TileContainer({color: color_amount - 1, wild_color: wild_tiles})

    def bonus_tile_lookup(self, star_color: int, position: int) -> int:
        """This uses the two lookup dictionaries in the PlayerBoard class to determine
        if a tile bonus is earned upon placing a tile.  Note here we're running into an index
        problem:  on the stars, the positions are labeled 0-5.  On the board, they're labeled
        1-6.  Should everything be 1-6?

        Args:
            tile_placed (key/value pair): The two-item object that stores the star and position of
            a tile just placed.

        Returns:
            int: Number of bonus tiles earned.
        """

        bonus_reward = 0
        colors_as_text = {RED: RED, ORANGE: ORANGE, YELLOW: YELLOW, GREEN: GREEN, BLUE: BLUE, PURPLE: PURPLE}
        tile_bonus_lookup = PlayerBoard.BONUSES_LOOKUP[f"{colors_as_text[star_color]}{position}"]
        for potential_bonus in tile_bonus_lookup:

            bonus_achieved = all(
                [
                    self.stars[tile[self.BONUS_STAR_INDEX]].filled_positions[
                        tile[self.BONUS_POS_INDEX]
                    ]
                    for tile in self.BONUS_CRITERIA[potential_bonus]["criteria"]
                ]
            )

            if bonus_achieved:
                bonus_reward += PlayerBoard.BONUS_CRITERIA[potential_bonus]["reward"]

        return bonus_reward

    def check_multistar_bonus(self, tile_placed_position: int) -> int:
        """This checks if a point bonus is received for placing all tiles of a particular
        number.  If every star on the board has a tile placed at the given position (given
        the position is less than 5), then the player receives a bonus equal to the position
        of the tile placed times the number of stars.

        Args:
            tile_placed_position (int): Position of tile placed, and bonus to check

        Returns:
            int: Points earned (either bonus or 0)
        """
        points_earned = 0
        if tile_placed_position < 5:
            points_earned = all(
                [
                    self.stars[color].filled_positions[tile_placed_position]
                    for color in self.stars.keys()
                ]
            ) * (tile_placed_position)
        return points_earned * PlayerBoard.FILL_ALL_POS_BONUS
