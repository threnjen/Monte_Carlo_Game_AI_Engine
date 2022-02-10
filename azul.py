# %%
from random import choice
from random import randrange
from itertools import combinations
from gui_test import display_stuff
from collections import Counter

master_tile_dictionary = {'red': 0,
                          "orange": 0, "yellow": 0, "green": 0, "blue": 0, "purple": 0}


def print_dict(print_dictionary: dict):
    """Prints a dictionary

    Args:
        print_dictionary (dict): To print

    Returns:
        str: Printed dictionary
    """
    return '\n'.join([f"{key}: {value}" for key, value in print_dictionary.items()])


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
        """Gets tiles in the container as a dictionary

        Returns:
            dict: dictionary of color : count pairs
        """
        return {color: self.tile_dictionary[color] for color in self.tile_dictionary.keys(
        ) if self.tile_dictionary[color] > 0}  # returns dictionary of tiles in the container
        # that are over 0

    def add_tiles(self, new_tiles: dict):
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

    def randomly_choose_tiles(self, take_count: int, tower: Tower):
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

        chosen_tiles = master_tile_dictionary.copy()
        for i in range(take_count):
            available_tiles = self.get_available_tiles()
            if not bool(available_tiles):
                self.tile_dictionary = tower.dump_all_tiles()
                available_tiles = self.get_available_tiles()
            color = choice(list(available_tiles.keys()))
            if color in chosen_tiles.keys():
                chosen_tiles[color] += 1
                self.tile_dictionary[color] -= 1
                self.tile_count -= 1
            else:
                raise f"Error:  invalid tilename passed ({color})"
        return chosen_tiles


class FactoryDisplay(TileContainer):
    """Each factory display stores tiles to be taken on a players turn.  Once tiles are
    taken, the remaining tiles are pushed to the center.

    Args:
        Tile_Container (Tile_Container): Parent class
    """

    def get_available_tiles(self, wild_color):
        tile_count = sum([cnt for cnt in self.tile_dictionary.values()])
        if self.tile_dictionary[wild_color] == tile_count and tile_count > 0:
            return {wild_color: tile_count}
        else:
            return {color: self.tile_dictionary[color] for color in self.tile_dictionary.keys(
            ) if all([self.tile_dictionary[color] > 0, color != wild_color])}
            # returns dictionary of tiles in the container
        # that are over 0

    def choose_tiles(self, chosen_color: str, wild_color: str):
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
        # available_tiles = self.get_available_tiles()

        # if chosen_color in available_tiles.keys():  # check if the chosen color is avail
        if chosen_color != wild_color:  # if the chosen color isn't the wild color,
            # set the chosen tiles = the chosen color
            chosen_tiles[chosen_color] = self.tile_dictionary[chosen_color]
            # set the display object for chosen color to 0
            self.tile_dictionary[chosen_color] = 0
            # if the wild color is also available
            if self.tile_dictionary[wild_color]:
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
        # else:  # return empty dict if chosen color is not avail
        # return {}, {}
        # else:
        #    raise f"Wild color {wild_color} is invalid"


class CenterOfTable(FactoryDisplay):
    """Center of table area (between factories).  Functions the same as a factory display,
    except that it stores the first player marker.  The tile choosing function is slightly
    different as a consequence.

    Args:
        FactoryDisplay (FactoryDisplay): Parent class
    """

    def __init__(self, tile_count=0, tile_dictionary=master_tile_dictionary):
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
        super(CenterOfTable, self).__init__(tile_count, tile_dictionary)
        self.first_player_avail = True

    def take_center_tiles(self, chosen_color: str, wild_color: str):
        """Same as choose_tiles from the FactoryDisplay class, except it returns
        the first player marker if available.
        Args:
            chosen_color (str): Chosen color
            wild_color (str): Wild color for the round

        Returns:
            dict: chosen_tiles, includes number of chosen color and 0 or 1 wild
            dict: leftover tiles, to be placed back in the center
            bool:  whether the first player marker is returned.
        """
        chosen_tiles, center_tiles = self.choose_tiles(
            chosen_color, wild_color)
        self.tile_dictionary = center_tiles
        if self.first_player_avail:
            self.first_player_avail = False
            return chosen_tiles, True
        else:
            return chosen_tiles, False

    def reset_first_player(self):
        self.first_player_avail = True


class Supply():
    tile_prefix = "supply"
    """Supply, which lives in the center of the scoreboard.


    """

    def __init__(self):
        """Generates the supply.  Default is to initialize an empty supply.
        """
        # super(Supply, self).__init__(tile_count, tile_dictionary)
        # self.tile_positions = {i: None for i in range(10)}
        self.tile_positions = []

    def get_tile_count(self):
        """Returns supply tile count

        Returns:
            int: tile count
        """
        return len(self.tile_positions)

    def fill_supply(self, tiles: dict):
        """Fills the supply with tiles from a dictionary.
        This is called after the get_tile_count method, so there isn't a risk of overfilling.

        Args:
            tiles (dict): dictionary of tile: count pairs.
        """
        for color, cnt in tiles.items():
            for tile in range(cnt):
                self.tile_positions.append(color)

    def get_legal_actions(self):
        """Gets the possible tiles we can pull

        Returns:
            dict: Dictionary of position : color pairs.
        """
        legal_actions = {pos: [self.tile_positions[pos], f"{self.tile_prefix}_{self.tile_positions[pos]}"]
                         for pos in range(len(self.tile_positions))}
        return legal_actions


class Factory(object):

    tile_prefix = "fact"

    def __init__(self, display_count):
        """Builds a factory, which contains a center and a number of displays,
        depending on the number players.  The display count is determined by the game
        class.

        Args:
            display_count (int): Number of displays to generate.
        """
        self.display_count = display_count
        # self.factory_displays = Dict[int, Factory]
        self.factory_displays = {i: FactoryDisplay()
                                 for i in range(display_count)}
        self.center = CenterOfTable()

    def take_from_display(self, display_number: int, chosen_color: str, wild_color: str):
        """Takes a tile from the given display and returns the tiles chosen and returns the tiles
        from that display (including a wild, unless the wild was the chosen color).  It puts the
        remaining tiles in the center location.  Note that wild cannot be
        taken if other tiles are present, and any color choice will also
        return one wild (if present)

        Args:
            display_number (int):  Display to take from
            chosen_color (str): Color to take
            wild_color (str): Wild for the round

        Returns:
            dict: received tiles
        """
        received_tiles, center_tiles = self.factory_displays[display_number].choose_tiles(
            chosen_color, wild_color)
        self.center.add_tiles(center_tiles)
        return received_tiles, False

    def take_from_center(self, chosen_color: str, wild_color: str):
        """Takes tiles from the center object.  Note that wild cannot be
        taken if other tiles are present, and any color choice will also
        return one wild (if present)

        Args:
            chosen_color (str): Color to take
            wild_color (str): Wild for the round

        Returns:
            dict: Dictionary of color: count pairs
        """
        return self.center.take_center_tiles(chosen_color, wild_color)

    def get_legal_actions(self, wild_color: str):
        """Gets available options in all factory displays and
        in the center.

        Args:
            wild_color (str): Wild color for the round

        Returns:
            dict: Dictionary of lists, with choice index : [color, count] pairs
        """
        tile_choices = {}
        i = 0
        for index, fact in self.factory_displays.items():
            for tile in fact.get_available_tiles(wild_color).keys():
                tile_choices[i] = [index, tile,
                                   f"{self.tile_prefix}_{index}_{tile}"]
                i += 1

        avail_tiles = self.center.get_available_tiles(wild_color)
        for tile in avail_tiles.keys():
            tile_choices[i] = [-1, tile,
                               f"{self.tile_prefix}_{-1}_{tile}"]
            i += 1

        return tile_choices

    def take_tiles(self, action, wild_color: str):
        """Takes tiles based on the action.  The action is derived from the
        get_available_tile_choices function, so can always be decoded.

        Args:
            action (list): [index, color] pairs
            wild_color (str): Wild color for the round

        Returns:
            dict:  tiles taken, as color: count pairs.  Note there can be at most two pairs
        """
        index = action[0]
        color = action[1]
        if index == -1:
            return self.take_from_center(color, wild_color)
        else:
            return self.take_from_display(index, color, wild_color)


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
        self.tile_positions = {i: False for i in range(1,
                                                       len(master_tile_dictionary) + 1)}
        self.star_full = False
        self.colors_allowed = {
            color: False for color in list(master_tile_dictionary.keys())}

        self.setup_colors_allowed()

    def setup_colors_allowed(self):
        """If the start type is all, we need to allow all colors initially.
        Afterward, we will restrict as tiles are placed.
        Otherwise, we will restrict to the single color of the star.  This seem
        redundant, but is to avoid different treatment for the "all" start later.

        """
        if self.color == "all":
            self.colors_allowed = {
                color: True for color in self.colors_allowed.keys()}
        else:
            self.colors_allowed[self.color] = True

    def add_tile(self, position: int, color: str):
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

        if self.colors_allowed[color] and not self.tile_positions[position]:
            self.tile_positions[position] = True
            if self.color == 'all':
                self.colors_allowed[color] = False
            if all([value for value in self.tile_positions.values()]):
                self.star_full = True
            points_earned = self.check_contiguous(position) + \
                self.star_full * Star.star_points[self.color]
            return points_earned
        else:
            return KeyError

    def check_left_contiguous(self, position: int):
        """Checks the number of contiguous tiles to the left and returns the point value,
        as though those were the only tiles.  We'll do right contiguous later.

        Args:
            position (int): Position of tile being placed.

        Returns:
            int: Points received (so far)
        """
        points = 1
        # This is terrible, but I had some dumb error I couldn't trace in my indices somewhere
        # in a different part of the code.  I'll fix this someday (ie. never)
        while self.tile_positions[(position - points) % 6 + (position == points) * 6]:
            points += 1
        return points

    def check_right_contiguous(self, position: int, points: int):
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
        while self.tile_positions[(position + distance) % 6 + (position + distance == 6) * 6]:
            points += 1
            distance += 1
        return points

    def check_contiguous(self, position: int):
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
        if points < 6:
            points = self.check_right_contiguous(position, points)
        return points

    def get_open_positions(self):
        """Gets open positions.  Note positions are stored as index: False
        until they are occupied (in other words, the tile_positions dictionary
        tracks positions that are currently filled with a tile, not open.)

        Returns:
            dict: position: occupied pairs.  Note all values will be False
        """
        return {pos: value for pos, value in self.tile_positions.items() if not value}


class PlayerBoard(object):
    """The player board stores the player stars, which in turn store the tiles placed.
    It may be best to have a function to add tiles to the star from here."""
    bonus_star_index = 0
    bonus_pos_index = 1
    action_star_index = 0
    action_tile_index = 1
    action_pos_index = 2
    tile_prefix = "star"
    bonuses_lookup = {"blue1": ["YBS"],
                      "blue2": ["YBS", "BAP"],
                      "blue3": ['BAP', 'BRS'],
                      "blue4": ['BRS'],
                      "blue5": ['BW'],
                      "blue6": ['BW'],
                      "red1": ['BRS'],
                      "red2": ['BRS', 'RAP'],
                      "red3": ['RAP', 'ROS'],
                      'red4': ['ROS'],
                      'red5': ['RW'],
                      'red6': ['RW'],
                      'orange1': ['ROS'],
                      'orange2': ['ROS', 'OAP'],
                      'orange3': ['OAP', 'OPS'],
                      'orange4': ['OPS'],
                      'orange5': ['OW'],
                      'orange6': ['OW'],
                      'purple1': ['OPS'],
                      'purple2': ['OPS', 'PAP'],
                      'purple3': ['PAP', 'PGS'],
                      'purple4': ['PGS'],
                      'purple5': ['PW'],
                      'purple6': ['PW'],
                      'green1': ['PGS'],
                      'green2': ['PGS', 'GAP'],
                      'green3': ['GAP', 'GYS'],
                      'green4': ['GYS'],
                      'green5': ['GW'],
                      'green6': ['GW'],
                      'yellow1': ['GYS'],
                      'yellow2': ['GYS', 'YAP'],
                      'yellow3': ['YAP', 'YBS'],
                      'yellow4': ['YBS'],
                      'yellow5': ['YW'],
                      'yellow6': ['YW'],
                      'all1': ['OAP', 'RAP'],
                      'all2': ['RAP', 'BAP'],
                      'all3': ['BAP', 'YAP'],
                      'all4': ['YAP', 'GAP'],
                      'all5': ['GAP', 'PAP'],
                      'all6': ['PAP', 'OAP'],
                      }

    bonus_criteria = {


        "BAP": {"criteria": [("blue", 2), ("blue", 3), ("all", 2), ("all", 3)],
                "reward": 1},
        'YAP': {"criteria": [("yellow", 2), ("yellow", 3), ("all", 2), ("all", 3)],
                "reward": 1},
        'GAP': {"criteria": [("green", 2), ("green", 3), ("all", 2), ("all", 3)],
                "reward": 1},
        'PAP': {"criteria": [("purple", 2), ("purple", 3), ("all", 2), ("all", 3)],
                "reward": 1},
        'OAP': {"criteria": [("orange", 2), ("orange", 3), ("all", 2), ("all", 3)],
                "reward": 1},
        'RAP': {"criteria": [("red", 2), ("red", 3), ("all", 2), ("all", 3)],
                "reward": 1},
        'OPS': {"criteria": [("orange", 3), ("orange", 4), ("purple", 1), ("purple", 2)],
                "reward": 2},
        'PGS': {"criteria": [("purple", 3), ("purple", 4), ("green", 1), ("green", 2)],
                "reward": 2},
        'GYS': {"criteria": [("green", 3), ("green", 4), ("yellow", 1), ("yellow", 2)],
                "reward": 2},
        'YBS': {"criteria": [("yellow", 3), ("yellow", 4), ("blue", 1), ("blue", 2)],
                "reward": 2},
        'BRS': {"criteria": [("blue", 3), ("blue", 4), ("red", 1), ("red", 2)],
                "reward": 2},
        'ROS': {"criteria": [("red", 3), ("red", 4), ("orange", 1), ("orange", 2)],
                "reward": 2},
        'OW': {"criteria": [("orange", 5), ("orange", 6)],
               "reward": 3},
        'PW': {"criteria": [("purple", 5), ("purple", 6)],
               "reward": 3},
        'GW': {"criteria": [("green", 5), ("green", 6)],
               "reward": 3},
        'YW': {"criteria": [("yellow", 5), ("yellow", 6)],
               "reward": 3},
        'BW': {"criteria": [("blue", 5), ("blue", 6)],
               "reward": 3},
        'RW': {"criteria": [("red", 5), ("red", 6)],
               "reward": 3},
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
        self.reserved_tiles = {}
        self.stars = {color: Star(color) for color in
                      list(master_tile_dictionary.keys()) + ["all"]}

    # def check_valid_position(self, star_color, tile_color, position):
    #     """Checks valid positions in a star.  Deprecated

    #     Args:
    #         star_color ([type]): [description]
    #         tile_color ([type]): [description]
    #         position ([type]): [description]

    #     Returns:
    #         [type]: [description]
    #     """
    #     try:
    #         star = self.stars[star_color]
    #         valid_position = not star.tile_positions[position]
    #         if star_color == "all":
    #             valid_color = star.colors_allowed[tile_color]
    #             return valid_position and valid_color
    #         else:
    #             return valid_position and (star_color == tile_color)
    #     except KeyError:
    #         return False

    def get_legal_actions(self, avail_tiles: dict, wild_color: str):
        """Probably the ugliest function I have so far.  This checks the legal placement of tiles
        based on the board position and the available tiles.

        Args:
            avail_tiles (dict): Tiles owned by the player
            wild_color (str): Wild color for the round

        Returns:
            dict: Dictionary of legal actions, indexed by integers.
        """
        avail_actions = {}
        i = 0
        # We need this to limit certain positions
        tot_tiles = sum([cnt for cnt in avail_tiles.values()])
        # for each star
        for star_index, star in self.stars.items():
            # We can only place if the star has a space for our color
            # We'll deal with the center star in a moment
            # This is an ugly hack.  I'm sorry.  Otherwise we get a key error
            # This hack isn't saved between function calls
            if star.color in avail_tiles.keys():
                color_avail = avail_tiles[star.color]
            if star.color == "all" or color_avail:
                open_pos = star.get_open_positions()
                # We need the positions open
                allowed_colors = [
                    color for color, open in star.colors_allowed.items() if open]
                for pos in open_pos.keys():
                    # We need this since our positions are different than our indices.
                    # I may correct this later.
                    if tot_tiles >= pos:
                        # We need this for the all star, which can't have two of the same color

                        for color in allowed_colors:
                            tile_name = f"{self.tile_prefix}_{self.player}_{star.color}_{pos}"
                            # We look at options to place that color
                            if (avail_tiles[color] + avail_tiles[wild_color] >= pos) and color != wild_color:
                                if avail_tiles[wild_color] and pos > 1:
                                    for j in range(1, min(avail_tiles[wild_color] + 1, pos)):
                                        if j + avail_tiles[color] >= pos:
                                            avail_actions[i] = [
                                                star_index, color, pos, pos - j, j, tile_name]
                                            i += 1
                                if avail_tiles[color] >= pos:
                                    avail_actions[i] = [
                                        star_index, color, pos, pos, 0, tile_name]
                            if avail_tiles[color] >= pos:
                                avail_actions[i] = [
                                    star_index, color, pos, pos, 0, tile_name]
                                i += 1

                            # If this is the wild color, we remove that many wilds

        return i, avail_actions

    def add_tile_to_star(self, action):
        """Adds a tile to star, checks for bonuses and points, and returns both.

        Args:
            star_color ([type]): [description]
            tile_color ([type]): [description]
            position ([type]): [description]

        Returns:
            [type]: [description]
        """
        star_color = action[self.action_star_index]
        tile_color = action[self.action_tile_index]
        position = action[self.action_pos_index]
        tile_points = self.stars[star_color].add_tile(position, tile_color)
        bonus_tile_count = self.bonus_tile_lookup(star_color, position)
        bonus_points = self.check_multistar_bonus(position)
        return bonus_tile_count, tile_points + bonus_points

    def begin_round(self):
        """This moves the tiles in the reserve to the temporary player supply.

        Returns:
            dictionary: Dictionary of tiles to place in the player supply.
        """

        to_player_supply = self.reserved_tiles.copy()
        self.reserved_tiles = {}
        return to_player_supply

    def bonus_tile_lookup(self, star_color: str, position: int):
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

        tile_bonus_lookup = PlayerBoard.bonuses_lookup[f"{star_color}{position}"]
        for potential_bonus in tile_bonus_lookup:

            bonus_achieved = all([self.stars[tile[self.bonus_star_index]].tile_positions[tile[self.bonus_pos_index]]
                                 for tile in self.bonus_criteria[potential_bonus]["criteria"]])

            if bonus_achieved:
                bonus_reward += PlayerBoard.bonus_criteria[potential_bonus]["reward"]

        return bonus_reward

    # def reserve_tiles(self, tile_dictionary: dict):
    #     """Adds tiles to the player reserve to hold between rounds.

    #     Args:
    #         tile_dictionary (dict): Dictionary of color/quantity pairs.

    #     Raises:
    #         f: Errors out if more than four tiles are passed.  Shouldn't happen, as this will
    #         be restricted elsewhere.
    #     """
    #     tiles_reserved = sum(
    #         [tile_count for tile_count in tile_dictionary.items()])
    #     if tiles_reserved > 4:
    #         raise f"Error:  too many tiles attempted to reserver ({tiles_reserved})"
    #     else:
    #         self.reserved_tiles = tile_dictionary.copy()

    def check_multistar_bonus(self, tile_placed_position: int):
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
            points_earned = all([self.stars[color].tile_positions[tile_placed_position]
                                 for color in self.stars.keys()]) * (tile_placed_position)
        return points_earned


class ScoreBoard(object):
    """Master scoreboard.  Only tracks player points and the round number.
    """

    def __init__(self, player_colors: int):
        """
        Not an interesting object

        Args:
            player_colors (dict): color/score pairs.  Scores are 5 to start.
        """
        self.player_colors = player_colors
        self.round_number = 0

    def increment_round(self):
        """Adds one to the round number
        """
        self.round_number += 1

    def increase_player_score(self, player, points):
        """Adds the points to the player color

        Args:
            player (str): Player color
            points (int): Points added (or removed)
        """
        self.player_colors[player] += points


class Player(object):
    starting_points = 5
    max_tile_reserve = 4
    player_colors = ["brown", "white", "black", "gray"]

    def __init__(self, player_ind: int, first_player=False):
        """Player, which is a surprisingly simple object so far.  The idea is that most actions
        will be controled outside of the player, since we can't pass objects in.

        Args:
            color (str): Player color
            first_player (bool, optional): Whether this is the first player. Defaults to False.
        """
        self.color = self.player_colors[player_ind]
        self.first_player = first_player
        self.player_tile_supply = master_tile_dictionary.copy()
        self.player_board = PlayerBoard(player_ind)
        self.player_score = Player.starting_points
        self.tile_count = 0
        self.legal_moves = {}
        self.bonus_earned = 0
        self.done_placing = False

    # I'm not sure it's valuable to have the player turn occur here rather than the game, but
    # I could see it being useful for passing control around.
    def change_player_supply(self, added_tiles: dict, method="add"):
        """Alters the amount of tiles in the player supply.

        Args:
            added_tiles (dict): Tiles to alter.
            method (optional, str): Whether we should add or remove tiles.  Default 'add'.
        """
        for color in added_tiles.keys():
            if method == "add":
                self.player_tile_supply[color] += added_tiles[color]
            elif method == "remove":
                self.player_tile_supply[color] -= added_tiles[color]

    def choose_tiles_to_reserve(self, tiles_to_choose=4, act_count=0):
        """We can only reserve four tiles, so this picks them.

        Args:
            tiles_to_choose (int, optional): [description]. Defaults to 4.
            act_count (int, optional): [description]. Defaults to 0.

        Returns:
            [type]: [description]
        """
        tiles = []
        for color, cnt in self.player_tile_supply.items():
            if cnt:
                tiles.extend([color] * cnt)
        choice_list = list(set(combinations(tiles, tiles_to_choose)))
        legal_moves = {}
        for option in choice_list:
            reserve_dict = {}
            for j in option:
                if j not in reserve_dict.keys():
                    reserve_dict[j] = 0
                reserve_dict[j] += 1
            legal_moves[act_count] = reserve_dict
            act_count += 1
        return legal_moves

    # def place_tiles(self, wild_color):
    #     total_tiles = self.get_tile_count()
    #     place_tile_input = input(f"""Select a location to place tiles.
    #     To enter your selection, enter a star_color, position on the star, tile color (which will
    #     match the star except for the center star),
    #     and number of wild ({wild_color} this round) tiles.  Enter "all" for the center star.
    #     Separate each input by a space.  As
    #     a reminder, you must use at least one matching tile, and you cannot place two of the same
    #     color in the center "all" star.  If you fail to select a valid move, you will receive this
    #     prompt again.
    #     If you are done placing tiles, return 0.  Currently, you have {total_tiles} remaining,
    #     and will lose {max(total_tiles-Player.max_tile_reserve, 0)} points and your excess
    #     tiles.  If this is the last round, you will lose all tiles and {total_tiles} points.
    #     """).split()

    #     return place_tile_input

    def get_tile_count(self):
        return sum([tile_count for tile_count in self.player_tile_supply.values()])

    def check_tile_supply(self, color: str, wilds_used: int, tiles_needed: int):
        """Confirms we have the correct number of tiles to cover a position.
        Used to determine legal moves.

        Args:
            color (str): Tile color
            wilds_used (int): Number of wilds we can use
            tiles_needed (int): Number of tiles needed

        Returns:
            bool: Player has sufficient tiles for position
        """
        return self.player_tile_supply[color] + wilds_used >= tiles_needed


class Game():
    """The game class will handle all aspects of the game.  All other objects will
    be instantiated in here.
    """
    tiles_per_factory = 4
    tiles_per_color = 22
    total_rounds = 6
    supply_max = 10
    reserve_max = 4
    wild_list = {1: "purple", 2: "green",
                 3: "orange", 4: "yellow", 5: "blue", 6: "red"}
    factory_req = {2: 5, 3: 7, 4: 9}
    first_player_cost = -2

    def __init__(self, player_count):
        """Builds the game from the player count.
        Args:
            player_count (int): Player count for this game.
        """
        self.player_count = player_count
        self.factory = Factory(Game.factory_req[player_count])
        self.supply = Supply()
        self.players = {i: Player(
            i) for i in range(self.player_count)}
        self.bag = Bag(
            132, {color: Game.tiles_per_color for color in master_tile_dictionary.keys()})
        self.tower = Tower()
        self.current_round = 1
        self.current_player_num = None
        self.first_player = None
        self.end_round = True
        self.place_tile_phase = False
        self.wild_color = None
        self.select_starting_player()
        self._state = None
        self.phase = 1
        self.start_round()
        self.game_over = False
        self.save_state()
        self.name = "Azul"

    def select_starting_player(self):
        """Called once at the beginning of the game.
        """
        self.first_player = randrange(0, self.player_count)
        self.players[self.first_player].first_player = True

    def fill_supply(self):
        """Fills the supply with tiles (up to 10).  Called at the beginning
        of the game, beginning of the round, and after a player is done placing tiles
        in phase two."""

        supply_count = self.supply.get_tile_count()
        self.supply.fill_supply(self.bag.randomly_choose_tiles(
            Game.supply_max - supply_count, self.tower))

    def get_legal_actions(self):
        """Called before every players turn.  Depends on the board state and current player.
        This shouldn't alter the game state except at the beginning of a round"""
        curr_player = self.players[self.current_player_num]
        if self.phase == 1:
            # Legal actions include taking tiles from the factory displays
            curr_player.legal_moves = self.factory.get_legal_actions(
                self.wild_color)
            return curr_player.legal_moves, self.current_player_num
        elif curr_player.bonus_earned:
            # Legal actions incluide taking tiles from the supply
            curr_player.legal_moves = self.supply.get_legal_actions()
            return curr_player.legal_moves.keys(), self.current_player_num
        else:
            # Legal actions include placing tiles on the player board or ending the turn
            player_tiles = curr_player.player_tile_supply
            curr_board = curr_player.player_board
            act_count, legal_moves = curr_board.get_legal_actions(
                player_tiles, self.wild_color)
            tile_count = sum([cnt for cnt in player_tiles.values()])
            if legal_moves and tile_count > 5:
                # To simplify for the bot, we don't allow a player to reserve tiles (and
                # end the turn) until they have five or fewer left or no other option
                pass
            else:
                # If there are four or fewer, there's no reserve choice to be made
                if tile_count <= 4:
                    legal_moves[act_count] = player_tiles
                else:
                    # Otherwise, we have to make a choice
                    legal_moves = {
                        **legal_moves, **curr_player.choose_tiles_to_reserve(4, act_count)}

            curr_player.legal_moves = legal_moves

            return list(legal_moves.keys()), self.current_player_num

    def start_round(self):
        """Begins a round (including the first one).

        Args:
            round (int): Round number
            wild_color (str): Wild color for the round.
        """
        self.select_starting_player()
        self.fill_supply()
        self.wild_color = Game.wild_list[self.current_round]
        for display in self.factory.factory_displays.values():
            tile_dict = self.bag.randomly_choose_tiles(
                Game.tiles_per_factory, self.tower)
            display.add_tiles(tile_dict)

        for player in self.players.values():
            player.change_player_supply(player.player_board.reserved_tiles)
            player.player_board.reserved_tiles = {}
        self.phase = 1
        self.current_player_num = self.first_player
        for player in self.players.values():
            player.done_placing = False
        self.factory.center.reset_first_player()
        self.save_state()
        # self.supply.refresh_positions()

    def update_game(self, action, player_num=-1):
        """Updates the game with a player action.  Note that an action can be
        multiple types depending on the action.  This is probably really bad.

        Args:
            action (var): Player action.
        """

        curr_player = self.players[self.current_player_num]
        sel_action = curr_player.legal_moves[action]
        if self.phase == 1:
            # If we're in phase one, the action is to take tiles from
            # a factory.  If there are tiles left after that, the next player
            # takes a turn.  Otherwise, the next player is whoever has the first
            # player token and we move to phase 2
            gained_tiles, first_player_change = self.factory.take_tiles(
                sel_action, self.wild_color)
            if first_player_change:
                self.first_player = self.current_player_num
                curr_player.player_score += self.first_player_cost
                curr_player.first_player = True
            curr_player.change_player_supply(gained_tiles)
            if self.factory.get_legal_actions(self.wild_color):
                self.current_player_num = (
                    self.current_player_num + 1) % self.player_count
            else:
                self.phase = 2
                self.current_player_num = self.first_player

        elif curr_player.bonus_earned:
            # If the player earned a bonus, the action is to take a tile from the
            # supply. We decrement the earned bonus by 1, add the tile to the player
            # supply, remove the tile from the global supply, and refresh the supply
            # tile count
            # Here, the sel_action is a tile color
            curr_player.change_player_supply(
                {self.supply.tile_positions.pop(action): 1})
            curr_player.bonus_earned -= 1

            # self.supply.refresh_positions()
        elif type(sel_action) is dict:
            # This is trickier.  The player can choose to stop placing tiles at any time.
            # If they do so, the action is a dictionary of tiles they would like to reserve
            # We check for that filetype, reserve the tiles, decrease player points (if
            # appropriate) reset the player tiles (reserves go to the player board), and
            # mark the player is done placing tiles.  This last step ensures that next time they
            # have a turn, it will be round 1 (see get_legal_moves)
            curr_player.player_board.reserved_tiles = sel_action
            curr_player.player_score += min(self.reserve_max -
                                            curr_player.get_tile_count(), 0)
            curr_player.player_tile_supply = master_tile_dictionary.copy()
            curr_player.done_placing = True
            self.current_player_num = (
                self.current_player_num + 1) % self.player_count
        else:
            # If they didn't stop placing tiles, they will place one here.
            # Remove the tiles from the player supply (using negatives),
            # add the tiles back to the tower, place the tiles, and collect
            # the bonuses and points.
            used_tiles = {}
            used_tiles[sel_action[1]
                       ] = sel_action[3]
            if sel_action[1] != self.wild_color:
                used_tiles[self.wild_color] = sel_action[4]

            curr_player.change_player_supply(used_tiles, method="remove")
            # This is a little clunky (reusing the dictionary), but seems cleaner
            # than creating a new one
            used_tiles[curr_player.legal_moves[action][1]] -= 1
            # We subtract one because one of the tiles stays on the player board.
            self.tower.add_tiles(used_tiles)
            # We pass the action array to the player board to add a tile and receive points
            # and a possible bonus back
            bonus_tile_count, points = curr_player.player_board.add_tile_to_star(
                curr_player.legal_moves[action])
            curr_player.bonus_earned = bonus_tile_count
            curr_player.player_score += points

        self.save_state()
        if all([player.done_placing for player in self.players.values()]):
            self.current_round += 1
            if self.current_round > self.total_rounds:
                self.game_over = True
                print(f"Game result: {print_dict(self.game_result())}")
            else:
                self.start_round()

    def is_game_over(self):
        return self.game_over

    def game_result(self):
        return {player_num: player.player_score for player_num, player in self.players.items()}

    def save_state(self):
        "Called at the end of every players action"
        self._state = f"Phase: {self.phase}\n"
        self._state += f"Current_player:  {self.current_player_num}\n"
        self._state += f"First player available: {self.factory.center.first_player_avail}\n"
        self._state += f"First player for next round: {self.first_player}\n"
        for key, disp in self.factory.factory_displays.items():
            self._state += f"Factory display {key} tiles:\n"
            self._state += f"{print_dict(disp.get_available_tiles(self.wild_color))}\n"
        self._state += "Center tiles: \n"
        self._state += f"{print_dict(self.factory.center.get_available_tiles(self.wild_color))}\n"
        self._state += "Supply tiles: \n"
        self._state += f"{self.supply.tile_positions}"
        for player_number, player in self.players.items():
            self._state += f"Player {player_number} score: {player.player_score}\n"
            self._state += f"Player {player_number} tiles:\n"
            self._state += f"{print_dict(player.player_tile_supply)}\n"
            for color, star in player.player_board.stars.items():
                if color == "all":
                    self._state += f"Player {player_number} {color} star avail colors:\n"
                    self._state += f"{print_dict(star.colors_allowed)}\n"
                self._state += f"Player {player_number} {color} star open positions: \n"
                self._state += f"{print_dict(star.get_open_positions())}\n"

    def prep_display(self):
        factory_dict = {}
        for ind, disp in self.factory.factory_displays.items():
            factory_dict[ind] = disp.tile_dictionary
        factory_dict[-1] = self.factory.center.tile_dictionary
        supply_dict = Counter(self.supply.tile_positions)
        player_dict = {}
        stars = {}
        for ind, player in self.players.items():
            player_dict[ind] = player.player_tile_supply
            stars[ind] = {}
            for star_ind, star in player.player_board.stars.items():
                stars[ind].update({star_ind: star.tile_positions})
        score_dict = {player_num: player.player_score for player_num,
                      player in self.players.items()}

        action = display_stuff(factory_dict, supply_dict,
                               player_dict, stars, self.players[self.current_player_num].legal_moves, score_dict)
        return action

    def play_game(self):
        """Plays the game (in the case where we are not using a bot)
        """
        while not self.is_game_over():
            self.get_legal_actions()
            # print(self._state)

            for key, value in self.players[self.current_player_num].legal_moves.items():
                print(f"{value}:  enter {key}")
            action = self.prep_display()
            # action = int(input("Choose an action"))
            self.update_game(action)


# %%
test = Game(2)
test.play_game()

# %%
