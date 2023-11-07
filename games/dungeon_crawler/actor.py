from typing import Any
from pydantic import BaseModel, Field, field_validator
from abc import ABC, abstractmethod
from card import DungeonCrawlerCard
import random


class Actor(BaseModel, ABC):
    # actor_deck: list[DungeonCrawlerCard] = Field(default_factory=list, validate_default=True)
    actor_health: int = None
    actor_defense: int = None
    actor_recovery: int = None
    actor_attack: int = None
    actor_movement: int = None
    actor_hand_limit: int = None
    actor_deck: list[DungeonCrawlerCard] = []
    actor_hand: list[DungeonCrawlerCard] = []
    actor_discard: list[DungeonCrawlerCard] = []

    # @field_validator("actor_deck")
    # @classmethod
    # def create_actor_deck(cls, actor_deck):
    #     if not actor_deck:
    #         random.shuffle(actor_deck)
    #     return actor_deck

    def model_post_init(self, __context: Any) -> None:
        random.shuffle(self.actor_deck)

    def begin_new_round(self):
        cards_to_draw = self.actor_hand_limit - len(self.actor_hand)
        if len(self.actor_deck) < cards_to_draw:
            print("Shuffling discard")
            random.shuffle(self.actor_discard)
            self.actor_deck.extend(self.actor_discard)
            self.actor_discard = []

        print("Drawing cards")
        for i in range(0, cards_to_draw):
            self.actor_hand.append(self.actor_deck.pop())
        print("Player hand:")
        print([x.name for x in self.actor_hand])
