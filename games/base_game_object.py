from abc import ABC, abstractmethod


class BaseGameObject(ABC):
    def __init__(self, player_count: int):
        """
        Initializes game.

        The following hooks are required in the Game __init__ file:
        game init must accept player_count argument (int)
        game init should declare a save_game dictionary (dict)

        Init in Game Object should first call super().__init__(player_count)
        """
        self.save_game = {}
        self.player_count = player_count
        self.game_over = False
        self.current_player = 0  # can be overridden in child class if this is determined differently (randomly etc). Must always be an int.
        self.scores = {
            x: 0 for x in range(0, player_count)
        }  # scores MUST live in this format of player: score in a dictionary. Can be overridden in child class for different presentation.

    def get_current_player(self) -> int:
        """
        Get currently available actions and active player to take an action from the list

        return active player ID as int
        """
        return self.current_player

    def get_game_scores(self):
        """
        Retrieves game score

        Must be a dictionary in format {playerID: Score}
        Where playerID matches IDs sent with get_legal_actions

        Returns:
            [dict]: dictionary in format playerID: score
        """
        return self.scores

    @abstractmethod
    def get_available_actions(self, special_policy: bool = False) -> list:
        """
        Hook #1
        Get currently available actions to take an action from the list

        Format [list of legal actions]

        The engine does not care about the contents of the list of legal actions, and will return
        a list item in exactly the same format it is passed. The game logic must manage the correct player turns. The Monte Carlo engine will assign the
        next legal action to the player passed, with no safety checks.
        """
        pass

    @abstractmethod
    def update_game_with_action(self, action: str, player: int) -> None:
        """
        Hook #2
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
        Hook #3
        Checks if game has ended

        Requires only True or False

        Returns:
            [True/False]: True/False if game is over
        """
        pass

    @abstractmethod
    def draw_board(self) -> None:
        """
        Hook #4
        Requests the game client draw a text representation of the game state

        Returns:
            draws game state
        """
        pass

    @abstractmethod
    def save_game_state(self) -> None:
        """
        Hook #5
        Saves the vital elements of the game to re-populate on load.

        The engine does not care about the format of the save state..
        The game logic must manage the usage of the save state and load state.
        Save your mutable game state objects here in the self.save_game dictionary
        Be sure to use DEEP COPIES, as efficiently as possible
        """
        pass

    @abstractmethod
    def load_save_game_state(self) -> None:
        """
        Hook #6
        load the saved game state.
        Be sure to use DEEP COPIES on load, as efficiently as possible
        """
        pass
