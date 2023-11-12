from numpy import ndarray
from typing import ClassVar, Union
from pydantic import BaseModel

class GameAction(ndarray):
    ACTION_SPACE_SIZE: ClassVar[int]