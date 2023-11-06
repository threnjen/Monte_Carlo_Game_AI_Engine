from typing_extensions import Unpack
from pydantic.config import ConfigDict
from game_components.base_game_object import BaseGameObject


class Battle(BaseGameObject):
    def get_available_actions(self, special_policy: bool = False) -> list:
        pass

    def update_game_with_action(self, action: str, player: int) -> None:
        pass

    def is_game_over(self) -> bool:
        pass

    def draw_board(self) -> None:
        pass

    def save_game_state(self) -> None:
        pass

    def load_save_game_state(self, dict) -> None:
        pass
