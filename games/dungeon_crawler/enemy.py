from pydantic import field_validator, Field
from actor import Actor
from card import DungeonCrawlerCard
from base_config import *
import random


class Enemy(Actor):
    actor_max_health: int = BASE_ENEMY_MAX_HEALTH
    actor_defense: int = BASE_ENEMY_DEFENSE
    actor_recovery: int = BASE_ENEMY_RECOVER
    actor_attack: int = BASE_ENEMY_ATTACK
    actor_movement: int = BASE_ENEMY_MOVEMENT
    actor_hand_limit: int = BASE_ROUND_ACTIONS
    actor_initiative: int = BASE_ENEMY_INITIATIVE
    actor_deck: list = ENEMY_DECK


if __name__ == "__main__":
    enemy = Enemy()
    print(enemy.actor_deck)
