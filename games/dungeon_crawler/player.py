from actor import Actor
from base_config import *
import random


class Player(Actor):
    # actor_deck: list[DungeonCrawlerCard] = Field(default_factory=list, validate_default=True)
    actor_max_health: int = BASE_PLAYER_MAX_HEALTH
    actor_defense: int = BASE_PLAYER_DEFENSE
    actor_recovery: int = BASE_PLAYER_RECOVER
    actor_attack: int = BASE_PLAYER_ATTACK
    actor_movement: int = BASE_PLAYER_MOVEMENT
    actor_hand_limit: int = BASE_PLAYER_HAND
    actor_deck: list = BASE_PLAYER_DECK
    actor_initiative: int = BASE_PLAYER_INITIATIVE
    round_number: int = 1

    def play_pretend_round(self):
        print(f"\nRound number: {self.round_number}")
        random.shuffle(self.actor_discard)
        for i in range(0, 3):
            self.actor_discard.append(self.actor_hand.pop())
        print("Player hand:")
        print([x.name for x in self.actor_hand])
        print(f"Cards in discard pile: {len(self.actor_discard)}")
        print(f"Cards in deck: {len(self.actor_deck)}")
        self.round_number += 1

    def get_available_card_hand(self):
        return self.actor_hand


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
    # print(player.actor_deck)
