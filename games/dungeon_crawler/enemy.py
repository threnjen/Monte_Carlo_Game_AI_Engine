from pydantic import BaseModel, field_validator, Field
from card import DungeonCrawlerCard
from base_config import *


class Enemy(BaseModel):
    enemy_deck: list[DungeonCrawlerCard] = Field(default_factory=list, validate_default=True)
    enemy_health: int = BASE_ENEMY_HEALTH
    enemy_defense: int = BASE_ENEMY_DEFENSE
    enemy_recovery: int = BASE_ENEMY_RECOVER
    enemy_attack: int = BASE_ENEMY_ATTACK
    enemy_movement: int = BASE_ENEMY_MOVEMENT

    @field_validator("enemy_deck")
    @classmethod
    def create_enemy_deck(cls, enemy_deck):
        if not enemy_deck:
            enemy_deck = ENEMY_DECK
        return enemy_deck


if __name__ == "__main__":
    enemy = Enemy()
    print(enemy.enemy_deck)
