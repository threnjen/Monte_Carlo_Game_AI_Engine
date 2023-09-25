from typing import ClassVar
# This is the right length for the vector, but it's possible the implementation is (very) wrong

import numpy as np
class AzulAction(np.ndarray):
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

    def __new__(cls):
        return np.zeros(cls.RESERVE_TILE_END, dtype=int).view(cls)