from pydantic import BaseModel

class ScoreBoard(BaseModel):
    """Master scoreboard.  Only tracks player points and the round number."""
    player_colors: dict[str, int]
    round_number: int = 0

    def increment_round(self):
        """Adds one to the round number"""
        self.round_number += 1

    def increase_player_score(self, player: int, points: int):
        """Adds the points to the player color

        Args:
            player (str): Player color
            points (int): Points added (or removed)
        """
        self.player_colors[player] += points
