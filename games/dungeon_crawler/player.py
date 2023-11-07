from pydantic import BaseModel, field_validator, Field
from card import DungeonCrawlerCard
from base_config import *
import random


class Player(BaseModel):
    player_deck: list[DungeonCrawlerCard] = Field(default_factory=list, validate_default=True)
    player_health: int = BASE_PLAYER_HEALTH
    player_defense: int = BASE_PLAYER_DEFENSE
    player_recovery: int = BASE_PLAYER_RECOVER
    player_attack: int = BASE_PLAYER_ATTACK
    player_movement: int = BASE_PLAYER_MOVEMENT
    player_hand: list[DungeonCrawlerCard] = []
    player_discard: list[DungeonCrawlerCard] = []
    round_number: int = 1

    @field_validator("player_deck")
    @classmethod
    def create_player_deck(cls, player_deck):
        if not player_deck:
            player_deck = BASE_PLAYER_DECK
            random.shuffle(player_deck)
        return player_deck

    def begin_new_round(self):
        cards_to_draw = BASE_PLAYER_HAND - len(self.player_hand)
        if len(self.player_deck) < cards_to_draw:
            print("Shuffling discard")
            random.shuffle(self.player_discard)
            self.player_deck.extend(self.player_discard)
            self.player_discard = []

        print("Drawing cards")
        for i in range(0, cards_to_draw):
            self.player_hand.append(self.player_deck.pop())
        print("Player hand:")
        print([x.name for x in self.player_hand])

    def play_pretend_round(self):
        print(f"\nRound number: {self.round_number}")
        random.shuffle(self.player_discard)
        for i in range(0, 3):
            self.player_discard.append(self.player_hand.pop())
        print("Player hand:")
        print([x.name for x in self.player_hand])
        print(f"Cards in discard pile: {len(self.player_discard)}")
        print(f"Cards in deck: {len(self.player_deck)}")
        self.round_number += 1

    def get_available_card_hand(self):
        return self.player_hand


if __name__ == "__main__":
    player = Player()
    player.begin_new_round()
    player.play_pretend_round()
    player.begin_new_round()
    player.play_pretend_round()
    player.begin_new_round()
    player.play_pretend_round()
    player.begin_new_round()
    player.play_pretend_round()
    player.begin_new_round()
    # print(player.player_deck)
