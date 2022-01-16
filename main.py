from random import choice

master_tile_dictionary = {'red': 0, "green": 0,
                          "orange": 0, "yellow": 0, "blue": 0, "purple": 0}


class TileContainer(object):
    """This can be used for both the tower and the bag.

    Args:
        object (object): Container that allows for additional and removal of tiles.
    """

    def __init__(self, tile_count=0, tile_dictionary=master_tile_dictionary):
        """The default object here is the tower.  For other objects, this can either be initialized
        with the bag keyword and defaults, or initialized with the correct parameters.
        Correct parameters can always be set later via the add_tiles method.

        Args:
            tile_count (int, optional): Default number of tiles. Defaults to 0, since
            most containers begin with zero tiles.
            tile_dictionary (dict, optional): Starting tile dictionary. Defaults to
            master_tile_dictionary
            The master_tile_dictionary gives the default keys in the dictionary.
        """
        self.tile_count = tile_count  # sets initial empty tile count on init
        # sets initial empty tile dictionary on init
        self.tile_dictionary = tile_dictionary.copy()

    def get_available_tiles(self):
        return {color: self.tile_dictionary[color] for color in self.tile_dictionary.keys(
        ) if self.tile_dictionary[color] > 0}  # returns dictionary of tiles in the container
        # that are over 0

    def add_tiles(self, new_tiles):
        """Adds tiles to the container, checking to make sure the keys are present.

        Args:
            new_tiles (dictionary): tiles to add

        Raises:
            f: Error when passed dictionary contains unknown key.
        """
        for color in new_tiles.keys():  # loop through color in new dictionary
            # TODO:  change to if/then (or find a way to reject new dictionary items)
            if color in self.tile_dictionary.keys():
                # update self tile dictionary
                self.tile_dictionary[color] += new_tiles[color]
                self.tile_count += new_tiles[color]
            else:
                # TODO:  this can be made into a generic error
                raise f"Error:  invalid tilename passed ({color})"


class Tower(TileContainer):
    """The tower is the container for tiles that have been used and discarded.
    It can be dumped into the bag

    Args:
        tile_container (tile_container): parent class
    """

    def dump_all_tiles(self):
        """This dumps tiles from the tower if possible.  Tiles only get dumped when drawing from the bag.
        If no tiles exist in the tower, this will return an empty dictionary, which will cause the
        caller to skip remaining attempts to draw from the bag.

        Returns:
            dictionary: Tiles dumped or an empty dictionary.
        """

        if bool(self.get_available_tiles()):  # check if available tiles exist
            # converts contents of Tower dictionary into a dump dictionary
            dump_tiles = self.tile_dictionary.copy()
            # resets tower dictionary to empty
            self.tile_dictionary = master_tile_dictionary.copy()
            self.tile_count = 0  # resets tower tile count to empty
            return dump_tiles  # returns dump tiles dict to game state to pass to Bag.add_tiles
        else:  # if no available tiles exist, returns empty dict
            return {}


class Bag(TileContainer):
    """The bag is where we draw tiles from.  We can take tiles directly from the bag (to either refill
    the supply or to fill the factory displays).

    Args:
        Tile_Container (Tile_Container): Parent class
    """

    def randomly_choose_tiles(self, take_count):
        """This allows us to take tiles from the bag. If there are insufficient tiles
        in the bag to take, it will return the dictionary of tiles chosen so far and the remaining
        take count.  The intent is for the player (or game) to then refill the bag from
        the tower and continue taking tiles.  This will only happen if remaining_tiles > 0.
        Note that when filling the bag, we should ensure the tower has tiles.

        Args:
            take_count (int): Number of tiles to take

        Raises:
            f: Error occurs when invalid key passed to the chosen_tiles dictionary; this can only
            occur if the container's tile dictionary somehow gets corrupted
            f: Error occurs when called on a tower object

        Returns:
            dict: dictionary of tiles chosen
            int: number of tiles yet taken
        """

        remaining_tiles = 0
        chosen_tiles = master_tile_dictionary.copy()
        for i in range(take_count):
            available_tiles = self.get_available_tiles()
            if bool(available_tiles):
                color = choice(list(available_tiles.keys()))
                if color in chosen_tiles.keys():
                    chosen_tiles[color] += 1
                    self.tile_dictionary[color] -= 1
                    self.tile_count -= 1
                else:
                    raise f"Error:  invalid tilename passed ({color})"
            else:  # if there are no tiles available to take
                remaining_tiles = take_count - i  # set the remaining tiles needed to draw
                break
        return chosen_tiles, remaining_tiles


class FactoryDisplay(TileContainer):
    """Each factory display stores tiles to be taken on a players turn.  Once tiles are
    taken, the remaining tiles are pushed to the center.

    Args:
        Tile_Container (Tile_Container): Parent class
    """

    def choose_tiles(self, chosen_color, wild_color):
        """We choose a color and take all tiles of that color.  Since players cannot skip,
        we return empty dictionarys if the color is not available.  This will force the player to
        choose another display or choose another color.  We also pass in the wild color for the
        round, since players must take exactly one wild tile in addition to their color choice
        if that tile is available.

        Args:
            chosen_color (str): Chosen color
            wild_color (str): Wild color for the round

        Raises:
            f: Error thrown when wild color passed is not valid.  Note this is not necessary
            for chosen colors, since chosen colors check against the universe of available
            tiles, not the universe of possible tiles.

        Returns:
            dict: chosen_tiles, includes number of chosen color and 0 or 1 wild
            dict: leftover tiles, to be placed in the center
        """
        chosen_tiles = {}
        # if wild_color in master_tile_dictionary.keys(): # I don't love this particular error check
        # but not sure how to revise atm.
        # I think because it would require the parent master tile dictionary to become corrupted;
        # if that happens the code is broken, so this check is redundant
        # get the tiles avail on the display object
        available_tiles = self.get_available_tiles()
        if chosen_color in available_tiles.keys():  # check if the chosen color is avail
            if chosen_color != wild_color:  # if the chosen color isn't the wild color,
                # set the chosen tiles = the chosen color
                chosen_tiles[chosen_color] = self.tile_dictionary[chosen_color]
                # set the display object for chosen color to 0
                self.tile_dictionary[chosen_color] = 0
                if wild_color in available_tiles.keys():  # if the wild color is also available
                    # add one wild to the chosen tiles
                    chosen_tiles[wild_color] = 1
                    # decrement display object by wild color by 1
                    self.tile_dictionary[wild_color] -= 1
            else:  # if the chosen color is the wild color
                # set chosen tiles to exactly 1 for that color
                chosen_tiles[chosen_color] = 1
                # decrement display object by wild color by 1
                self.tile_dictionary[chosen_color] -= 1
            # make a copy of tiles in display object to send to senter
            send_to_center = self.tile_dictionary.copy()
            # reset this display object to empty
            self.tile_dictionary = master_tile_dictionary.copy()
            return chosen_tiles, send_to_center
        else:  # return empty dict if chosen color is not avail
            return {}, {}
        # else:
        #    raise f"Wild color {wild_color} is invalid"


class CenterOfTable(FactoryDisplay):
    """Center of table area (between factories).  Functions the same as a factory display,
    except that it stores the first player marker.  The tile choosing function is slightly
    different as a consequence.

    Args:
        FactoryDisplay (FactoryDisplay): Parent class
    """

    def __init__(self, tile_count=0, tile_dictionary=master_tile_dictionary, first_player_avail=True):
        """Same as factory display, but now takes an optional first_player_avail argument.
        I don't see a case where this would be false on init, but we'll keep it general for now.

        Args:
            tile_count (int, optional): Default number of tiles. Defaults to 0 since the center
            begins with zero tiles
            tile_dictionary (dict, optional): Starting tile dictionary. Defaults to
            master_tile_dictionary The master_tile_dictionary gives the default keys in the
            dictionary.
            first_player_avail (bool, optional): Denotes whether the first player marker is
            available.Defaults to True.
        """
        FactoryDisplay.__init__(tile_count, tile_dictionary)
        self.first_player_avail = first_player_avail

    def choose_center_tiles(self, chosen_color, wild_color):
        """Same as choose_tiles from the FactoryDisplay class, except it returns
        the first player marker if available.
        Args:
            chosen_color (str): Chosen color
            wild_color (str): Wild color for the round

        Returns:
            dict: chosen_tiles, includes number of chosen color and 0 or 1 wild
            dict: leftover tiles, to be placed in the center
            bool:  whether the first player marker is returned.
        """
        chosen_tiles, center_tiles = self.choose_tiles(
            chosen_color, wild_color)
        if self.first_player_avail:
            self.first_player_avail = False
            return chosen_tiles, center_tiles, True
        else:
            return chosen_tiles, center_tiles, False


class Supply(TileContainer):
    """Supply.  Note: we only need the tile positions for display
    purposes should we choose to animate the game.  Otherwie, it doesn't matter how we
    order the tiles.

    Args:
        TileContainer ([type]): [description]
    """

    def __init__(self, tile_count=0, tile_dictionary=master_tile_dictionary):
        TileContainer.__init__(tile_count, tile_dictionary)
        self.tile_positions = {i: None for i in range(10)}

    def refresh_positions(self):

        pos = 0
        temp_tiles = self.tile_dictionary.copy()

        for color in temp_tiles.keys():
            while temp_tiles[color] > 0:
                if pos > 10:
                    raise "Error:  more tiles than spaces available."
                else:
                    self.tile_positions[pos] = color
                    temp_tiles[color] -= 1
                    pos += 1


class Star(object):
    """Player board star.  There are seven possible:  six colors and one colorless,
    denoted here as 'all'.  The primary action here is to add a tile, and the primary
    return is the points received.

    Args:
        object (object): Star on player board.
    """
    star_points = {'red': 14, "green": 18,
                   "orange": 17, "yellow": 16, "blue": 15, "purple": 20, "all": 12}

    def __init__(self, color):
        """The only unique starting property of the star is the color, since points are from
        the class variable.  Otherwise, all stars are the same.  Their position is controlled
        by the player board, so all bonus tile received are also controlled by the player board.

        Args:
            color (string): Star color
        """
        self.color = color
        self.tile_postions = {i: False for i in range(
            len(master_tile_dictionary))}
        self.star_full = False
        self.colors_allowed = {
            color: False for color in master_tile_dictionary.keys()}

    def setup_colors_allowed(self):
        """If the start type is all, we need to allow all colors initially.
        Afterward, we will restrict as tiles are placed.
        Otherwise, we will restrict to the single color of the star.  This seem
        redundant, but is to avoid different treatment for the "all" start later.

        Raises:
            f: Invalid start color.  This should never occur.
        """
        if self.color in self.colors_allowed.keys() + "all":
            if self.color == "all":
                self.colors_allowed = {
                    color: True for color in self.colors_allowed.keys()}
            else:
                self.colors_allowed[self.color] = True
        else:
            raise f"Invalid star color {self.color}"

    def add_tile(self, position, color):
        """Adds a tile to the board at a given position.
        This can only be done if the position is empty and if the
        player has the required tiles.  However, the tile requirement
        check is done elsewhere.

        Args:
            position (int): Position to place tile
            color (str): Tile color placed.

        Raises:
            f: Position already occupied.  This shouldn't trigger since this is checked outside.
            f: Invalid color.  This shouldn't trigger since it's checked elsewhere.

        Returns:
            int: Points gained from tile placement, including completing the star if applicable.
        """
        if self.tile_position[position]:
            raise f"Error:  tile already exists in position {position}"
        else:
            if self.colors_allowed[color]:
                self.tile_position[position] = True
                if self.color == 'all':
                    self.colors_allowed[color] = False
                if all([item for item in self.tile_positions.items()]):
                    self.star_full = True
                return self.check_contiguous[position] + self.star_full * Star.star_points[self.color]
            else:
                raise f"Error:  invalid color {color} for star {self.color}"

    def check_left_contiguous(self, position):
        """Checks the number of contiguous tiles to the left and returns the point value,
        as though those were the only tiles.  We'll do right contiguous later.

        Args:
            position (int): Position of tile being placed.

        Returns:
            int: Points received (so far)
        """
        points = 1
        while self.tile_position[(position - points) % 6]:
            points += 1
        return points

    def check_right_contiguous(self, position, points):
        """Checks the number of right contiguous tiles and returns the point value, in addition
        to the left-contiguous tiles.

        Args:
            position (int): Position of tile placed.
            points (int): Points

        Returns:
            int: Points
        """
        distance = 1
        while self.tile_position[(position + distance) % 6]:
            points += 1
            distance += 1
        return points

    def check_contiguous(self, position):
        points = self.check_left_contiguous(position)
        if points < 6:
            points = self.check_right_contiguous(position)
        return points


class PlayerBoard(object):

    bonuses_lookup = {"blue1": ["BYS"], "blue2": ["BYS", "BAP"],
                      }

    bonus_criteria = {
        "BAP": {"criteria": [("blue", 2), ("blue", 3), ("all", 2), ("all", 3)],
                "reward": 2}
    }

    def __init__(self, player_color, first_plyaer=False):
        self.player_color = player_color
        self.first_player = first_plyaer
        self.reserved_tiles = {}
        self.stars = master_tile_dictionary.copy() + {"all": 0}

    def setup_stars(self):
        for color in self.stars.keys():
            self.stars[color] = Star(color).setup_colors_allowed()

    def bonus_lookup(self, tile_placed):

        bonus_reward = 0

        tile_bonus_lookup = PlayerBoard.bonuses_lookup[tile_placed]
        for potential_bonus in tile_bonus_lookup:

            bonus_achieved = all([self.stars[tile[0]].tile_position[tile[1]]
                                  for tile in PlayerBoard.bonus_criteria[potential_bonus]["criteria"]])

            if bonus_achieved:
                bonus_reward += PlayerBoard.bonus_criteria[potential_bonus]["reward"]

        return bonus_reward
