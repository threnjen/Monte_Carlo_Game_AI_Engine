from distutils.command.build_scripts import first_line_re
from doctest import master
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
            tile_count (int, optional): Default number of tiles. Defaults to 0, since the most containers
            begin with zero tiles.
            tile_dictionary (dict, optional): Starting tile dictionary. Defaults to master_tile_dictionary
            The master_tile_dictionary gives the default keys in the dictionary.
        """
        self.tile_count = tile_count
        self.tile_dictionary = tile_dictionary.copy()

    def get_available_tiles(self):
        return {color: self.tile_dictionary[color] for color in self.tile_dictionary.keys(
        ) if self.tile_dictionary[color] > 0}

    def add_tiles(self, new_tiles):
        """Adds tiles to the container, checking to make sure the keys are present.

        Args:
            new_tiles (dictionary): tile dictionary to add

        Raises:
            f: Error when passed dictionary contains unknown key.
        """
        for color in new_tiles.keys():
            if color in self.tile_dictionary:
                self.tile_dictionary[color] += new_tiles[color]
                self.tile_count += new_tiles[color]
            else:
                # TODO:  this can be made into a generic error
                raise f"Error:  invalid tilename passed to {self.container_type} ({color})"


class Tower(TileContainer):
    """The tower is the container for tiles that have been used and discarded.  It can be dumped into the bag

    Args:
        tile_container (tile_container): parent class
    """

    def dump_all_tiles(self):
        """This dumps tiles from the tower if possible.  Tiles only get dumped when drawing from the bag.
        If no tiles exist in the tower, this will return an empty dictionary, which will cause the caller to skip
        remaining attempts to draw from the bag.

        Returns:
            dictionary: Tiles dumped or an empty dictionary.
        """

        if bool(self.get_available_tiles()):
            dump_tiles = self.tile_dictionary.copy()
            self.tile_dictionary = master_tile_dictionary.copy()
            self.tile_count = 0
            return dump_tiles
        else:
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
            f: Error occurs when invalid key passed to the chosen_tiles dictionary; this can only occur
            if the container's tile dictionary somehow gets corrupted
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
                else:
                    raise f"Error:  invalid tilename passed ({color})"
            else:
                remaining_tiles = take_count - i
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
        if wild_color in master_tile_dictionary.keys():
            available_tiles = self.get_available_tiles()
            if chosen_color in available_tiles.keys():
                if chosen_color != wild_color:
                    chosen_tiles[chosen_color] = self.tile_dictionary[chosen_color]
                    self.tile_dictionary[chosen_color] = 0
                    if wild_color in available_tiles.keys():
                        chosen_tiles[wild_color] = 1
                        self.tile_dictionary[wild_color] -= 1
                else:
                    chosen_tiles[chosen_color] = 1
                    self.tile_dictionary[chosen_color] -= 1
                center_tiles = self.tile_dictionary.copy()
                self.tile_dictionary = None
                return chosen_tiles, center_tiles
            else:
                return {}, {}
        else:
            raise f"Wild color {wild_color} is invalid"


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
            tile_count (int, optional): Default number of tiles. Defaults to 0, since the most containers
            begin with zero tiles.
            tile_dictionary (dict, optional): Starting tile dictionary. Defaults to master_tile_dictionary
            The master_tile_dictionary gives the default keys in the dictionary.
            first_player_avail (bool, optional): Denotes whether the first player marker is available.
            Defaults to True.
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
