from typing import ClassVar
from games.game_components.action import GameAction
import numpy as np

class AzulAction(GameAction):
    PHASE_1_START: ClassVar[int] = 0
    PHASE_1_END: ClassVar[int] = 16
    PHASE_2_START: ClassVar[int] = 16
    PHASE_2_END: ClassVar[int] = 53
    FACTORY_START: ClassVar[int] = 0
    FACTORY_END: ClassVar[int] = 9
    CENTER_START: ClassVar[int] = 9
    CENTER_END: ClassVar[int] = 10
    FACTORY_TAKE_COLOR_START: ClassVar[int] = 10
    FACTORY_TAKE_COLOR_END: ClassVar[int] = 16
    STAR_START: ClassVar[int] = 16
    STAR_END: ClassVar[int] = 23
    STAR_POINT_START: ClassVar[int] = 23
    STAR_POINT_END: ClassVar[int] = 29
    STAR_SPEND_COLOR_START: ClassVar[int] = 29
    STAR_SPEND_COLOR_END: ClassVar[int] = 35
    BONUS_START: ClassVar[int] = 35
    BONUS_END: ClassVar[int] = 41
    TILE_START: ClassVar[int] = 41
    TILE_END: ClassVar[int] = 47
    RESERVE_TILE_START: ClassVar[int] = 47
    RESERVE_TILE_END: ClassVar[int] = 53
    ACTION_SPACE_SIZE: ClassVar[int] = 53

    def __new__(cls):
        return np.zeros(cls.ACTION_SPACE_SIZE, dtype=int).view(cls)

    @property
    def factory_take_color(self) -> int:
        return np.argmax(
            self[
                AzulAction.FACTORY_TAKE_COLOR_START : AzulAction.FACTORY_TAKE_COLOR_END
            ]
        )

    @property
    def take_from_displays_ind(self) -> bool:
        return self[AzulAction.FACTORY_START : AzulAction.FACTORY_END].max() == 1

    @property
    def display_take_number(self) -> int:
        return np.argmax(self[AzulAction.FACTORY_START : AzulAction.FACTORY_END])

    @property
    def tile_placement_action_ind(self) -> int:
        return sum(self[AzulAction.STAR_START : AzulAction.STAR_END]) == 1

    @property
    def take_bonus_tiles_ind(self) -> int:
        return sum(self[AzulAction.BONUS_START : AzulAction.BONUS_END]) > 0

    @property
    def reserve_tile_action_ind(self) -> int:
        return (
            sum(self[AzulAction.RESERVE_TILE_START : AzulAction.RESERVE_TILE_END]) > 0
        )

    @property
    def star_to_place_tile(self) -> int:
        return np.argmax(self[AzulAction.STAR_START : AzulAction.STAR_END])

    @property
    def position_to_place_tile(self) -> int:
        return np.argmax(self[AzulAction.STAR_POINT_START : AzulAction.STAR_POINT_END])

    @property
    def wilds_to_spend(self, wild_color: int) -> int:
        return self[AzulAction.STAR_SPEND_COLOR_START + wild_color]

    @property
    def non_wilds_to_spend(self, wild_color: int) -> int:
        return sum(
            self[AzulAction.STAR_SPEND_COLOR_START : AzulAction.STAR_SPEND_COLOR_END]
        ) - self.wilds_to_spend(wild_color)

    @property
    def tile_color_to_place(self, wild_color: int) -> int:
        temp_array = self[
            AzulAction.STAR_SPEND_COLOR_START : AzulAction.STAR_SPEND_COLOR_END
        ].copy()
        temp_array[wild_color] = 0
        return np.argwhere(temp_array > 0)

    @property
    def tiles_to_reserve(self) -> dict:
        return {
            i: self[AzulAction.RESERVE_TILE_START + i]
            for i in range(AzulAction.RESERVE_TILE_END - AzulAction.RESERVE_TILE_START)
        }
