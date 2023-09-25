from __future__ import annotations
from collections import Counter
from random import sample
from games.azul.action import AzulAction
from itertools import combinations

RED = 0
ORANGE = 1
YELLOW = 2
GREEN = 3
BLUE = 4
PURPLE = 5


MASTER_TILE_CONTAINER = Counter(
    {
        RED: 0,
        ORANGE: 0,
        YELLOW: 0,
        GREEN: 0,
        BLUE: 0,
        PURPLE: 0,
    }
)

class TileContainer(Counter):
    """Tile containers represent all game objects that can hold tiles.
    """
    def model_dump_json(self) -> dict:
        return dict(self)

    def randomly_choose_tiles(self, number_to_choose: int) -> TileContainer:
        """Randomly choose tiles from the container

        Raises:
            ValueError: Number to choose cannot be greater than the number of elements.

        Returns:
            TileContainer:  regardless of child class, we only return a TileContainer
        """
        # TODO:  Remove Value error
        # We need to look into where this should be an error and where it should return the remaining tiles.
        if number_to_choose > self.total():
            raise ValueError(
                f"Cannot choose {number_to_choose} from only {self.total()} tiles."
            )
        chosen_tiles = TileContainer(sample(list(self.elements()), number_to_choose))
        self.subtract(chosen_tiles)
        return chosen_tiles

    def remove_all_tiles(self) -> TileContainer:
        """Removes tiles in the container and returns them.

        Returns:
            TileContainer: _description_
        """
        remaining_tiles = TileContainer(self.elements())
        self.clear()
        return remaining_tiles

class Bag(TileContainer):
    """The bag is where we draw tiles from.  We can take tiles directly from the bag (to either refill
    the supply or to fill the factory displays).

    It is possible for the bag to run out of tiles.  In this case, we take refill from the tower.
    If, after a refill, the bag is still out of tiles, this is acceptable.

    """

    def randomly_choose_tiles(
        self, take_count: int, tower: TileContainer
    ) -> dict[str, int]:
        """This allows us to take tiles from the bag. If there are insufficient tiles
        in the bag to take, we take all tiles in the bag, refill from the tower, and then
        continue taking tiles.  If the bag again runs out, only return the tiles in the bag.

        Args:
            take_count (int): Number of tiles to take
        """

        chosen_tiles = MASTER_TILE_CONTAINER.copy()

        if self.total() < take_count:
            chosen_tiles = TileContainer(self.elements())
            self.tiles = tower.remove_all_tiles()
            take_count = take_count - chosen_tiles.total()
        try:
            chosen_tiles += super().randomly_choose_tiles(take_count)
        except ValueError:
            chosen_tiles = self.remove_all_tiles()
        return chosen_tiles


class FactoryDisplay(TileContainer):
    """Each factory display stores tiles to be taken on a player_count turn.  Once tiles are
    taken, the remaining tiles are pushed to the center.

    Args:
        Tile_Container (Tile_Container): Parent class
    """

    def take_chosen_tiles(
        self, chosen_color: int, wild_color: int
    ) -> tuple[dict[str, int], dict[str, int]]:
        """We choose a color and take all tiles of that color.  Since player_count cannot skip,
        we return empty dictionarys if the color is not available.  This will force the player to
        choose another display or choose another color.  We also pass in the wild color for the
        round, since player_count must take exactly one wild tile in addition to their color choice
        if that tile is available.

        Args:
            chosen_color (int): Chosen color
            wild_color (int): Wild color for the round

        Returns:
            dict: chosen_tiles, includes number of chosen color and 0 or 1 wild
            dict: leftover tiles, to be placed in the center
        """
        chosen_tiles = MASTER_TILE_CONTAINER.copy()
        if chosen_color != wild_color:
            chosen_tiles[chosen_color] = self.get(chosen_color, 0)
            if self[wild_color] > 0:
                chosen_tiles[wild_color] = 1
        else:
            chosen_tiles[chosen_color] = 1
        self.subtract(chosen_tiles)
        return chosen_tiles

    def get_available_actions(self, wild_color: int) -> list[AzulAction]:
        """Lists all possible actions for the factory display.  This includes taking all tiles of
        a given color or taking a wild tile (if present).

        Args:
            wild_color (int): Wild color for the round

        Returns:
            list: List of potential actions
        """
        actions = []

        for color in self.keys():
            if self[color] == 0:
                continue
            action = AzulAction()
            # We can't take wild colors if other colors are present
            if color == wild_color and (self[wild_color] != self.total()):
                continue
            action[AzulAction.FACTORY_TAKE_COLOR_START + color] = self[color]
            # If we don't have a wild color, we're allowed to take one if it's present
            if self[wild_color] > 0 and color != wild_color:
                action[AzulAction.FACTORY_TAKE_COLOR_START + wild_color] = 1
            actions.append(action)
        return actions


class CenterOfFactory(FactoryDisplay):
    """Center of table area (between factories).  Functions the same as a factory display,
    except that it stores the first player marker.  The tile choosing function is slightly
    different as a consequence.

    Args:
        FactoryDisplay (FactoryDisplay): Parent class
    """

    def __init__(self, *args, **kwargs):
        """Same as factory display, but now takes an optional first_player_avail argument.
        I don't see a case where this would be false on init.

        Args:
            tile_count (int, optional): Default number of tiles. Defaults to 0 since the center
            begins with zero tiles
            tile_dictionary (dict, optional): Starting tile dictionary. Defaults to
            master_tile_dictionary The master_tile_dictionary gives the default keys in the
            dictionary.
            first_player_avail (bool, optional): Denotes whether the first player marker is
            available.Defaults to True.
        """
        super().__init__(*args, **kwargs)
        self._first_player_avail = True

    def model_dump_json(self) -> dict:
        return super().model_dump_json() | {"first_player_avail": self._first_player_avail}

    def reset_first_player(self):
        self._first_player_avail = True

    def get_first_player_avail(self) -> bool:
        return self._first_player_avail

    def take_first_player(self):
        first_player = self._first_player_avail
        self._first_player_avail = False
        return first_player


class Supply(TileContainer):
    """Supply, which lives in the center of the scoreboard.
    """

    def fill_supply(self, fill_tiles: TileContainer):
        """Fills the supply with tiles from a dictionary.
        This is called after the get_tile_count method, so there isn't a risk of overfilling.

        Args:
            tiles (dict): dictionary of tile: count pairs.
        """
        self += fill_tiles

    def get_available_actions(self, num_tiles_to_take: int) -> list[AzulAction]:
        """Lists all possible actions for the supply.  This includes taking all tiles of
        a given color or taking a wild tile (if present).

        Args:
            num_tiles_to_take (int): Number of tiles to take

        Returns:
            list: List of potential actions
        """

        if num_tiles_to_take >= self.total():
            action = AzulAction()
            for color in self.keys():
                action[AzulAction.BONUS_START + color] = self[color]
            return [action]
        combinations_list = list(combinations(list(self.elements()), num_tiles_to_take))
        actions = []
        for combination in combinations_list:
            action = AzulAction()
            for color in combination:
                action[AzulAction.BONUS_START + color] += 1
            actions.append(action)