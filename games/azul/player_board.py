from azul.tile_container import MASTER_TILE_CONTAINER, TileContainer

class Star:
    """Player board star.  There are seven possible:  six colors and one colorless,
    denoted here as 'all'.  The primary action here is to add a tile, and the primary
    return is the points received.

    Args:
        object (object): Star on player board.
    """

    STAR_POINTS = {
        "red": 14,
        "green": 18,
        "orange": 17,
        "yellow": 16,
        "blue": 15,
        "purple": 20,
        "all": 12,
    }
    STAR_SIZE = 6

    def __init__(self, color: str):
        """The only unique starting property of the star is the color, since points are from
        the class variable.  Otherwise, all stars are the same.  Their position is controlled
        by the player board, so all bonus tile received are also controlled by the player board.

        Args:
            color (string): Star color
        """
        self.color = color
        self.tile_positions = {i: False for i in range(1, self.STAR_SIZE)}
        self.star_full = False
        self.colors_allowed = {
            color: False for color in MASTER_TILE_CONTAINER.keys()
        }

        self.setup_colors_allowed()

    def setup_colors_allowed(self):
        """If the start type is all, we need to allow all colors initially.
        Afterward, we will restrict as tiles are placed.
        Otherwise, we will restrict to the single color of the star.  This seem
        redundant, but is to avoid different treatment for the "all" start later.

        """
        if self.color == "all":
            self.colors_allowed = {color: True for color in self.colors_allowed.keys()}
        else:
            self.colors_allowed[self.color] = True

    def place_tiles_on_star(self, position: int, color: str) -> int:
        """Adds a tile to the board at a given position.
        This can only be done if the position is empty and if the
        player has the required tiles.  However, the tile requirement
        check is done elsewhere.

        Args:
            position (int): Position to place tile
            color (str): Tile color placed.

        Returns:
            int: Points gained from tile placement, including completing the star if applicable.
        """

        self.tile_positions[position] = True
        if self.color == "all":
            self.colors_allowed[color] = False
        if all([value for value in self.tile_positions.values()]):
            self.star_full = True
        points_earned = (
            self.check_contiguous(position)
            + self.star_full * Star.STAR_POINTS[self.color]
        )
        return points_earned

    def check_left_contiguous(self, position: int) -> int:
        """Checks the number of contiguous tiles to the left and returns the point value,
        as though those were the only tiles.  We'll do right contiguous later.

        Args:
            position (int): Position of tile being placed.

        Returns:
            int: Points received (so far)
        """
        points = 1
        for points in range(1, self.STAR_SIZE + 1):
            if self.tile_positions[(position - points - 1) % self.STAR_SIZE + 1]:
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
        # This is terrible, but I had some dumb error I couldn't trace in my indices somewhere
        # in a different part of the code.  I'll fix this someday (ie. never)
        for distance in range(1, self.STAR_SIZE):
            if self.tile_positions[(position + distance - 1) % self.STAR_SIZE + 1]:
                points += 1
            else:
                return points
        return self.STAR_SIZE

    def check_contiguous(self, position: int) -> int:
        """Checks both left and right contiguous from a given position.
        This is used to determine points when placing a tile.  Note this is
        really annoying because star positions are 1-6, not 0-5 (see the
        individual functions)

        Args:
            position (int): position to check

        Returns:
            int: Points earned
        """
        points = self.check_left_contiguous(position)
        if points < self.STAR_SIZE:
            points = self.check_right_contiguous(position, points)
        return points


class PlayerBoard:
    """The player board stores the player stars, which in turn store the tiles placed.
    It may be best to have a function to add tiles to the star from here."""

    BONUS_STAR_INDEX = 0
    BONUS_POS_INDEX = 1
    ACTION_STAR_INDEX = 0
    ACTION_TILE_INDEX = 1
    ACTION_POS_INDEX = 2
    TILE_PREFIX = "star"
    BONUSES_LOOKUP = {
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

    BONUS_CRITERIA = {
        "BAP": {
            "criteria": [("blue", 2), ("blue", 3), ("all", 2), ("all", 3)],
            "reward": 1,
        },
        "YAP": {
            "criteria": [("yellow", 2), ("yellow", 3), ("all", 2), ("all", 3)],
            "reward": 1,
        },
        "GAP": {
            "criteria": [("green", 2), ("green", 3), ("all", 2), ("all", 3)],
            "reward": 1,
        },
        "PAP": {
            "criteria": [("purple", 2), ("purple", 3), ("all", 2), ("all", 3)],
            "reward": 1,
        },
        "OAP": {
            "criteria": [("orange", 2), ("orange", 3), ("all", 2), ("all", 3)],
            "reward": 1,
        },
        "RAP": {
            "criteria": [("red", 2), ("red", 3), ("all", 2), ("all", 3)],
            "reward": 1,
        },
        "OPS": {
            "criteria": [("orange", 3), ("orange", 4), ("purple", 1), ("purple", 2)],
            "reward": 2,
        },
        "PGS": {
            "criteria": [("purple", 3), ("purple", 4), ("green", 1), ("green", 2)],
            "reward": 2,
        },
        "GYS": {
            "criteria": [("green", 3), ("green", 4), ("yellow", 1), ("yellow", 2)],
            "reward": 2,
        },
        "YBS": {
            "criteria": [("yellow", 3), ("yellow", 4), ("blue", 1), ("blue", 2)],
            "reward": 2,
        },
        "BRS": {
            "criteria": [("blue", 3), ("blue", 4), ("red", 1), ("red", 2)],
            "reward": 2,
        },
        "ROS": {
            "criteria": [("red", 3), ("red", 4), ("orange", 1), ("orange", 2)],
            "reward": 2,
        },
        "OW": {"criteria": [("orange", 5), ("orange", 6)], "reward": 3},
        "PW": {"criteria": [("purple", 5), ("purple", 6)], "reward": 3},
        "GW": {"criteria": [("green", 5), ("green", 6)], "reward": 3},
        "YW": {"criteria": [("yellow", 5), ("yellow", 6)], "reward": 3},
        "BW": {"criteria": [("blue", 5), ("blue", 6)], "reward": 3},
        "RW": {"criteria": [("red", 5), ("red", 6)], "reward": 3},
    }

    def __init__(self, player_num: int):
        """Note that we don't copy the reseverd tiles dictionary from
        the master_tile_dictionary.  We can only ever reserve four tiles;
        there's no need to have all six spots reserved.

        Args:
            player_color (str): Player color
            first_plyaer (bool, optional): Whether this is the first player. Defaults to False.
        """
        self.player = player_num
        self.reserved_tiles = TileContainer()
        self.stars = {
            color: Star(color)
            for color in list(MASTER_TILE_CONTAINER.keys()) + ["all"]
        }

    def add_tile_to_star(self, star_color: str, tile_color: str, position: str) -> tuple[int]:
        """Adds a tile to star, checks for bonuses and points, and returns both.

        Args:
            star_color ([type]): [description]
            tile_color ([type]): [description]
            position ([type]): [description]

        Returns:
            [type]: [description]
        """
        tile_points = self.stars[star_color].place_tiles_on_star(position, tile_color)
        bonus_tile_count = self.bonus_tile_lookup(star_color, position)
        bonus_points = self.check_multistar_bonus(position)
        return bonus_tile_count, tile_points + bonus_points

    def begin_round_for_player(self):
        """This moves the tiles in the reserve to the temporary player supply.

        Returns:
            dictionary: Dictionary of tiles to place in the player supply.
        """

        return self.reserved_tiles.remove_all_tiles()

    def bonus_tile_lookup(self, star_color: str, position: int) -> int:
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

        tile_bonus_lookup = PlayerBoard.BONUSES_LOOKUP[f"{star_color}{position}"]
        for potential_bonus in tile_bonus_lookup:

            bonus_achieved = all(
                [
                    self.stars[tile[self.BONUS_STAR_INDEX]].tile_positions[
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
        number.  Note that again tile position range (0-5 or 1-6) is causing a problem:
        since bonuses are 4 * the tile position value, we need to add one to the tile position.
        This is really making me think we should have the range be 1-6.

        Args:
            tile_placed_position (int): Position of tile placed, and bonus to check

        Returns:
            int: Points earned (either bonus or 0)
        """
        points_earned = 0
        if tile_placed_position < 5:
            points_earned = all(
                [
                    self.stars[color].tile_positions[tile_placed_position]
                    for color in self.stars.keys()
                ]
            ) * (tile_placed_position)
        return points_earned