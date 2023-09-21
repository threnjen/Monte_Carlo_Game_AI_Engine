import games.azul.tile_container as tc
from pydantic import BaseModel, Field
from typing import ClassVar


class Factory(BaseModel):
    model_config = {"arbitrary_types_allowed": True}
    tile_prefix: ClassVar[str] = "fact"
    display_count: int
    factory_displays: dict[int, tc.FactoryDisplay] = None
    center: tc.CenterOfFactory = Field(default_factory=tc.CenterOfFactory)

    def is_factory_empty(self) -> bool:
        factory_display_total_tiles = sum(
            display.total() for display in self.factory_displays.values()
        )
        return factory_display_total_tiles + self.center.total() == 0

    def model_post_init(self, __context) -> None:
        if self.factory_displays is None:
            self.factory_displays = {
                i: tc.FactoryDisplay() for i in range(self.display_count)
            }

    def populate_factory_display(self, display_num: int, tiles: tc.TileContainer):
        self.factory_displays[display_num] += tiles

    def take_from_factory_display(
        self, display_number: int, chosen_color: str, wild_color: str
    ) -> tuple:
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
        received_tiles = self.factory_displays[display_number].take_chosen_tiles(
            chosen_color, wild_color
        )
        self.center += self.factory_displays[display_number].remove_all_tiles()
        return received_tiles

    def take_from_factory_center(self, chosen_color: str, wild_color: str):
        """Takes tiles from the center object.  Note that wild cannot be
        taken if other tiles are present, and any color choice will also
        return one wild (if present)

        Args:
            chosen_color (str): Color to take
            wild_color (str): Wild for the round

        Returns:
            dict: Dictionary of color: count pairs
        """
        return (
            self.center.take_chosen_tiles(chosen_color, wild_color),
            self.center.take_first_player(),
        )
