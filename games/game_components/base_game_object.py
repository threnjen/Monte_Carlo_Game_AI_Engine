from abc import ABC, abstractmethod
from .player import Player as BasePlayer
from pydantic import BaseModel

class GameEnvironment(BaseModel):
    player_count: int
    players: dict[int, BasePlayer] = None

    @abstractmethod
    def get_current_player(self) -> int:
        """
        Hook #1
        Get currently available actions and active player to take an action from the list

        return active player ID as int
        """
        pass

    @abstractmethod
    def get_available_actions(self, special_policy: bool = False) -> list:
        """
        Hook #2
        Get currently available actions to take an action from the list

        Format [list of legal actions]

        The engine does not care about the contents of the list of legal actions, and will return
        a list item in exactly the same format it is passed. The game logic must manage the correct player turns. The Monte Carlo engine will assign the
        next legal action to the player passed, with no safety checks.
        """
        pass

    @abstractmethod
    def update_game_with_action(self, action: str, player: int):
        """
        Hook #3
        Sends action choice and player to game

        After selecting an item from the list of legal actions (see Hook #1),
        Sends the item back to the game logic. Item is sent back in exactly
        the same format as received in the list of legal actions.

        Also sends active player ID for action

        Args:
            action (list item): selected item from list of legal actions
            player (int): player number
        """
        pass

    @abstractmethod
    def is_game_over(self) -> bool:
        """
        Hook #4
        Checks if game has ended

        Requires only True or False

        Returns:
            [True/False]: True/False if game is over
        """
        pass

    @abstractmethod
    def get_game_scores(self) -> dict:
        """
        Hook #5
        Retrieves game score

        Must be a dictionary in format {playerID: Score}
        Where playerID matches IDs sent with get_legal_actions

        Returns:
            [dict]: dictionary in format playerID: score
        """
        pass

    @abstractmethod
    def board(self):
        """
        Hook #6
        Requests the game client draw a text representation of the game state

        Returns:
            draws game state
        """
        pass

    @abstractmethod
    def get_game_state(self) -> tuple:
        """Hook #7
        Requests the game client to return a tuple representing a completely unique game state.

        Returns:
            tuple: Game state.  Tuple must contain strings and integers (it will be hashed later)
        """
        pass

    @abstractmethod
    def update_game_state(self, game_state: tuple):
        """Hook #8
        Gives the game a game state, allowing a partially played game to be created.
        tuple must be in the same format as the one returned in get_game_state
        """