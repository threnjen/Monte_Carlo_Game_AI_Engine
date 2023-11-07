from pydantic import Field, field_validator
from actor import Actor
from base_config import *
from card import *
import random


class Enemy(Actor):
    actor_max_health: int = BASE_ENEMY_MAX_HEALTH
    actor_defense: int = BASE_ENEMY_DEFENSE
    actor_recovery: int = BASE_ENEMY_RECOVER
    actor_attack: int = BASE_ENEMY_ATTACK
    actor_movement: int = BASE_ENEMY_MOVEMENT
    actor_hand_limit: int = BASE_ROUND_ACTIONS
    actor_initiative: int = BASE_ENEMY_INITIATIVE
    actor_deck: list = Field(default_factory=list, validate_default=True)
    enemy_specials: dict = SAMPLE_ENEMY_SPECIALS

    @field_validator("actor_deck")
    @classmethod
    def create_actor_deck(cls, actor_deck):
        actor_deck = BASE_ENEMY_DECK
        for i in range(0, 3):
            for special_name, special_attributes in SAMPLE_ENEMY_SPECIALS.items():
                actor_deck.append(
                    SPECIAL_CARD_TYPE[special_attributes.get("type")](
                        name=special_name, modifier=special_attributes.get("modifier")
                    )
                )
        return actor_deck


if __name__ == "__main__":
    enemy = Enemy()
    print(enemy.actor_deck)
