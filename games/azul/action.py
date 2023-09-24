# This is the right length for the vector, but it's possible the implementation is (very) wrong
class AzulAction(list):
    PHASE_1_START = 0
    PHASE_1_END = 16

    PHASE_2_START = 16
    PHASE_2_END = 53
    FACTORY_START = 0
    FACTORY_END = 9
    CENTER_START = 9
    CENTER_END = 10
    FACTORY_TAKE_COLOR_START = 10
    FACTORY_TAKE_COLOR_END = 16
    STAR_START = 16
    STAR_END = 23
    STAR_POINT_START = 23
    STAR_POINT_END = 29
    STAR_SPEND_COLOR_START = 29
    STAR_SPEND_COLOR_END = 35
    BONUS_START = 35
    BONUS_END = 41
    TILE_START = 41
    TILE_END = 47
    SAVE_TILE_START = 47
    SAVE_TILE_END = 53
    COLORS = {'red':0, 'orange':1, 'yellow':2, 'green':3, 'blue':4, 'purple':5}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if len(self) == 0:
            self.extend([0] * self.PHASE_2_END)