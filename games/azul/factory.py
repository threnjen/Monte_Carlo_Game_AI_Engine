import games.azul.tile_container as tc
from pydantic import BaseModel, Field
from typing import ClassVar
from .action import AzulAction
import numpy as np

class Factory(BaseModel):
    model_config = {"arbitrary_types_allowed": True}
    tile_prefix: ClassVar[str] = "fact"
    center_size: ClassVar[int] = 1
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
        self, display_number: int, chosen_color: int, wild_color: int
    ) -> tuple:
        """Takes a tile from the given display and returns the tiles chosen and returns the tiles
        from that display (including a wild, unless the wild was the chosen color).  It puts the
        remaining tiles in the center location.  Note that wild cannot be
        taken if other tiles are present, and any color choice will also
        return one wild (if present)

        Args:
            display_number (int):  Display to take from
            chosen_color (int): Color to take
            wild_color (int): Wild for the round

        Returns:
            dict: received tiles
        """
        received_tiles = self.factory_displays[display_number].take_chosen_tiles(
            chosen_color, wild_color
        )
        self.center += self.factory_displays[display_number].remove_all_tiles()
        return received_tiles

    def take_from_factory_center(self, chosen_color: int, wild_color: int) -> tuple[tc.TileContainer, bool]:
        """Takes tiles from the center object.  Note that wild cannot be
        taken if other tiles are present, and any color choice will also
        return one wild (if present)

        Args:
            chosen_color (int): Color to take
            wild_color (int): Wild for the round

        Returns:
            dict: Dictionary of color: count pairs
        """
        return (
            self.center.take_chosen_tiles(chosen_color, wild_color),
            self.center.take_first_player(),
        )

    def get_available_actions(self, wild_color: int) -> list[AzulAction]:
        """Lists all potential actions for the factory.  This includes taking from any factory
        display or the center. 

        Returns:
            list: List of potential actions
        """
        actions = []
        for display in self.factory_displays.values():
            actions.append(
                display.get_available_actions(wild_color)
            )
        actions.append(
            self.center.get_available_actions(wild_color))
        return actions

    def update_game_with_action(self, action: AzulAction, wild_color: int) -> tuple[tc.TileContainer, bool]:
        """Plays the action.  The action
        is assumed to be valid.  It returns the tiles taken and the first player
        marker (if taken).

        Args:
            action (AzulAction): Action to take

        Returns:
            tuple: Tiles taken and first player marker
        """
        take_color = np.argmax(action[AzulAction.FACTORY_TAKE_COLOR_START: AzulAction.FACTORY_TAKE_COLOR_END])
        if action[AzulAction.FACTORY_START: AzulAction.FACTORY_END].max() == 1:
            factory_num = np.argmax(action[AzulAction.FACTORY_START: AzulAction.FACTORY_END])
            return self.take_from_factory_display(factory_num, take_color, wild_color), False
        else:
            return self.take_from_factory_center(
                take_color, wild_color
            )
