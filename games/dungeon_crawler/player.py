from .actor import Actor
from .base_config import *
import random
from itertools import permutations
from .battle_grid import BattleGrid

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
    _round_number: int = 1
    score: int = 0

    def play_pretend_round(self):
        print(f"\nRound number: {self._round_number}")
        random.shuffle(self.actor_discard)
        for i in range(0, 3):
            self.actor_discard.append(self.actor_hand.pop())
        print(f"Player hand: {[x.name for x in self.actor_hand]}")
        print(f"Cards in discard pile: {len(self.actor_discard)}")
        print(f"Cards in deck: {len(self.actor_deck)}")
        self._round_number += 1

    def _replenish_deck(self):
        """Replace the deck with the discard pile, and shuffle.  This is called when
        the deck is empty and the player needs to draw cards.  Players are required
        to exhaust their draw before they can shuffle their discard pile, so the
        fshuffled discard is appended to the end of."""
        random.shuffle(self.actor_discard)
        self.actor_deck.extend(self.actor_discard)
        self.actor_discard = []

    def get_available_actions(self, actions_required_this_round: int) -> list:
        """Return a list of all possible actions for the player to take this round.
        This is a list of all permutations of the player's hand, with the length of
        the permutation equal to the number of actions required this round.
        If a player can not take any actions, they are dead.
        
        Args:
            actions_required_this_round (int): The number of actions the player
                must take this round.
        
        Returns:
            list: A list of all possible permutations of the player's hand."""
        action_names = [x.name for x in self.actor_hand if x.type != "junk"]
        all_perms = [x for x in permutations(action_names, actions_required_this_round)]
        unique_perms = list(set(all_perms))
        if unique_perms == []:
            self.is_dead = True
        return unique_perms

    def _execute_attack(self, target: Actor):
        """Players execute attacks by reducing the target's health by the player's
        attack value.  If the target's health is reduced to 0, the target is dead."""
        target.actor_current_health -= self.actor_attack
        target.actor_current_health = max(0, target.actor_current_health)
        if target.actor_current_health == 0:
            target.is_dead = True

    def play_card_to_stack(self, action_set):
        print(f"Chosen action set: {action_set}")

        def execute_action(action):
            item_index = 0
            for card in self.actor_hand:
                if card.name == action:
                    card = self.actor_hand.pop(item_index)
                    self.round_stack.append(card)
                    break
                item_index += 1

        for action in action_set:
            execute_action(action)

        print(f"Remaining hand: {[x.name for x in self.actor_hand]}")
        print(f"Actions in stack: {[x.name for x in self.round_stack]}")

    def play_action(self, actors: list[Actor], battle_grid: BattleGrid):
        action = self.round_stack.pop()
        if action.type == "move":
            self.move(action, self.actors, self.battle_grid)
        elif action.type == "attack":
            self.attack(action, self.actors)
        else:
            raise ValueError(f"Unknown card type: {action.type}")
        # elif action.type == "defend":
        #     self.defend(action)
        # elif action.type == "recover":
        #     self.recover(action)


    def _resolve_move_when_adjacent(self, actors: list[Actor]):
        """This is called when the player is adjacent to an enemy.  The player
        will move away from the enemy, if possible.  If the player is surrounded
        by enemies, they will not move.  They will also not move if there is no
        position available where after a move they are not adjacent to an enemy.
        
        Args:
            actors (list[Actor]): The list of all actors in the game."""
        # TODO:  simplify this.  Seems complicated right now.
        original_position = self.location_on_grid
        if self.location_on_grid[0] > 0:
            self.location_on_grid = (self.location_on_grid[0] - 1, self.location_on_grid[1])
            neighbor_list = self._get_enemy_neighbors(actors)
            if neighbor_list == []:
                return
            else:
                self.location_on_grid = original_position
        # TODO:  need to pass in grid size
        if self.location_on_grid[0] < 4:
            self.location_on_grid = (self.location_on_grid[0] + 1, self.location_on_grid[1])
            neighbor_list = self._get_enemy_neighbors(actors)
            if neighbor_list == []:
                return
            else:
                self.location_on_grid = original_position
        if self.location_on_grid[1] > 0:
            self.location_on_grid = (self.location_on_grid[0], self.location_on_grid[1] - 1)
            neighbor_list = self._get_enemy_neighbors(actors)
            if neighbor_list == []:
                return
            else:
                self.location_on_grid = original_position
        if self.location_on_grid[1] < 4:
            self.location_on_grid = (self.location_on_grid[0], self.location_on_grid[1] + 1)
            neighbor_list = self._get_enemy_neighbors(actors)
            if neighbor_list == []:
                return
            else:
                self.location_on_grid = original_position

if __name__ == "__main__":
    player = Player()
    player.begin_new_round()
    avail_actions = player.get_available_actions(3)
    action = avail_actions.pop()
    player.play_card_to_stack(action)
