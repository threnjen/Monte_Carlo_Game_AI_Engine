from pydantic import field_validator, Field
from actor import Actor
from card import DungeonCrawlerCard
from base_config import *


class Enemy(Actor):
    actor_deck: list[DungeonCrawlerCard] = Field(default_factory=list, validate_default=True)
    actor_health: int = BASE_ENEMY_HEALTH
    actor_defense: int = BASE_ENEMY_DEFENSE
    actor_recovery: int = BASE_ENEMY_RECOVER
    actor_attack: int = BASE_ENEMY_ATTACK
    actor_movement: int = BASE_ENEMY_MOVEMENT
    actor_hand_limit: int = BASE_ROUND_ACTIONS
    actor_deck: list = ENEMY_DECK
    actor_hand: list[DungeonCrawlerCard] = []
    actor_discard: list[DungeonCrawlerCard] = []

    @field_validator("actor_deck")
    @classmethod
    def create_actor_deck(cls, actor_deck):
        if not actor_deck:
            actor_deck = ENEMY_DECK
        return actor_deck


if __name__ == "__main__":
    enemy = Enemy()
    print(enemy.actor_deck)
