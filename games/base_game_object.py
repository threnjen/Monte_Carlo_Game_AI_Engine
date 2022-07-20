from abc import ABC, abstractmethod

class BaseGameObject(ABC):

    def __init__(self, player_count):
        """
        Initializes game.

        The following hooks are required in the Game __init__ file:
        game init must accept player_count argument (int)
        """
        self.player_count = player_count
    
    @abstractmethod
    def get_legal_actions(self, policy:bool=False):
        """
        Hook #1
        Get currently available actions and active player to take an action from the list

        Requires return of a list with two indices:
        0: list of legal actions
        1: active player ID

        Format [[list of legal actions], active player ID]

        The engine does not care about the contents of the list of legal actions, and will return
        a list item in exactly the same format it is passed. The game logic must manage the correct player turns. The Monte Carlo engine will assign the
        next legal action to the player passed, with no safety checks.

        Returns:
            [list]: List of: list of legal actions and active player ID
        """
        pass

    @abstractmethod
    def update_game(self):
        """
        Hook #2
        Sends action choice and player to game

        After selecting an item from the list of legal actions (see Hook #1),
        Sends the item back to the game logic. Item is sent back in exactly
        the same format as received in the list of legal actions.

        Also returns active player ID for action

        Args:
            action (list item): selected item from list of legal actions
            player (int): player number
        """
        pass

    @abstractmethod
    def is_game_over(self):
        """
        Hook #3
        Checks if game has ended

        Requires only True or False

        Returns:
            [True/False]: True/False if game is over
        """
        pass

    @abstractmethod
    def game_result(self):
        """
        Hook #4
        Retrieves game score

        Must be a dictionary in format {playerID: Score}
        Where playerID matches IDs sent with get_legal_actions

        Returns:
            [dict]: dictionary in format playerID: score
        """
        pass

    @abstractmethod
    def draw_board(self):
        """
        Hook #5
        Requests the game client draw a text representation of the game state

        Returns:
            draws game state
        """
        pass

