from games.game_components.action import GameAction
from typing import ClassVar

class TicTacToeAction(GameAction):
    """Tic tac toe action"""
    ACTION_SPACE_SIZE: ClassVar[int] = 9

    @property
    def position(self) -> int:
        return self.argmax()