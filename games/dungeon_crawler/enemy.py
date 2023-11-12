from pydantic import Field, field_validator
from .actor import Actor
from .base_config import *
from .card import *
import random
from  .battle_grid import BattleGrid

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
    required_action_count: int = 3

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

    def _replenish_deck(self):
        """Monster replenish deck is different than player replenish deck.  Monsters
        shuffle their discard pile with their deck.  Players shuffle their
        discard pile and add it to the bottom of deck.  This way players are
        forced to see all cards, but monsters are not.  This eliminates some
        card counting."""
        self.actor_discard.append(self.actor_deck)
        self.actor_deck = []
        random.shuffle(self.actor_discard)
        self.actor_deck.extend(self.actor_discard)
        self.actor_discard = []

    def _execute_attack(self, target: Actor):
        """Monster attacks add junk to the player discard."""
        return target.actor_discard.append(JunkCard(name="Junk", modifier=0))

    def play_turn(self, actors: list[Actor], battle_grid: BattleGrid):
        """Plays the monsters turn.  Some monsters will have special abilities that
        require additional logic.  For now, we ignore this.
        
        Args:
            actors (list[Actor]): The list of actors in the battle
            battle_grid (BattleGrid): The battle grid
        
        Reminders:
            Monster cards are chosen randomly when drawn, and individual cards are
            drawn randomly from the hand.  The random draw must occur when the card
            is executed to support AI."""
        selected_card = self.actor_hand.pop(random.randrange(0, len(self.actor_hand)))
        if selected_card.type == "attack":
            self.attack(selected_card, actors)
        elif selected_card.type == "move":
            self.move(selected_card, actors, battle_grid)
        # elif selected_card.type.startswith("special"):
        else:
            raise ValueError(f"Unknown card type: {selected_card.type}")

    # Enemy deck size should be 11

if __name__ == "__main__":
    enemy = Enemy()
    print(enemy.actor_deck)
