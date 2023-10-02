from numpy import ndarray
from typing import ClassVar

class GameAction(ndarray):
    ACTION_SPACE_SIZE: ClassVar[int]