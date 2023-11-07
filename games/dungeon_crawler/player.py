from pydantic import BaseModel, field_validator, Field
from card import DungeonCrawlerCard
from base_decks import BASE_PLAYER_DECK


class Player(BaseModel):
    player_deck: list[DungeonCrawlerCard] = Field(default_factory=list, validate_default=True)

    @field_validator("player_deck")
    @classmethod
    def create_player_deck(cls, player_deck):
        if not player_deck:
            player_deck = BASE_PLAYER_DECK
        return player_deck


if __name__ == "__main__":
    player = Player()
    print(player.player_deck)
