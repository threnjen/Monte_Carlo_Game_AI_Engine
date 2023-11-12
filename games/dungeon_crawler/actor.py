from __future__ import annotations
from typing import Any, Union
from pydantic import BaseModel
from abc import ABC, abstractmethod
from .card import DungeonCrawlerCard
import random
from .action import DungeonCrawlerAction
from .battle_grid import BattleGrid
import numpy as np
import heapq


class Node(BaseModel):
    row: int
    col: int
    g: float = 0  # Cost from start node to current node
    h: float = 0  # Heuristic (estimated cost from current node to goal node)
    f: float = 0  # Total cost: f = g + h
    parent: Node = None

    def __eq__(self, other: object) -> bool:
        return self.f == other.f

    def __lt__(self, other: object) -> bool:
        return self.f < other.f

    def __gt__(self, other: object) -> bool:
        return self.f > other.f


def astar(
    map: np.ndarray, start: tuple[int, int], end: tuple[int, int]
) -> list[tuple[int, int]]:
    """A* pathfinding algorithm implementation.
    map: 2D array of integers. 0 = unoccupied, 1 = occupied
    start: tuple of (row, col) for start node
    end: tuple of (row, col) for end node
    See https://en.wikipedia.org/wiki/A*_search_algorithm for details.
    """

    rows, cols = len(map), len(map[0])

    def is_valid(node: Node):
        return (
            0 <= node.row < rows
            and 0 <= node.col < cols
            and map[node.row][node.col] == 0
        )

    def heuristic(node: Node, end: Node):
        return abs(node.row - end.row) + abs(node.col - end.col)

    open_set: list[Node] = []
    closed_set: set[Node] = set()

    start_node = Node(row=start[0], col=start[1])
    end_node = Node(row=end[0], col=end[1])

    if not is_valid(start_node) or not is_valid(end_node):
        return None

    # We store in a heap for efficiency
    # The heap will store tuples of (f_score, node)
    heapq.heappush(open_set, (start_node.f, start_node))

    while open_set:
        current_node = heapq.heappop(open_set)[1]

        if current_node.row == end_node.row and current_node.col == end_node.col:
            path: list[tuple[int, int]] = []
            while current_node:
                path.append((current_node.row, current_node.col))
                current_node = current_node.parent
            return path[::-1]  # Return reversed path

        closed_set.add((current_node.row, current_node.col))

        neighbors = [
            Node(row=current_node.row - 1, col=current_node.col),
            Node(row=current_node.row + 1, col=current_node.col),
            Node(row=current_node.row, col=current_node.col - 1),
            Node(row=current_node.row, col=current_node.col + 1),
        ]

        # TODO: Add weight to moves that pass through allies
        # This will allow for pathfinding through allies, but
        # will also prefer to move around allies if both are unique.
        for neighbor in neighbors:
            if is_valid(neighbor) and (neighbor.row, neighbor.col) not in closed_set:
                neighbor.g = current_node.g + 1
                neighbor.h = heuristic(neighbor, end_node)
                neighbor.f = neighbor.g + neighbor.h
                neighbor.parent = current_node

                heapq.heappush(open_set, (neighbor.f, neighbor))

    return None  # No path found


class Actor(BaseModel, ABC):
    model_config = {"arbitrary_types_allowed": True}
    # actor_deck: list[DungeonCrawlerCard] = Field(default_factory=list, validate_default=True)
    actor_max_health: int = None
    actor_current_health: int = actor_max_health
    actor_defense: int = None
    actor_recovery: int = None
    actor_attack: int = None
    actor_movement: int = None
    actor_hand_limit: int = None
    actor_initiative: int = None
    actor_deck: list[DungeonCrawlerCard] = []
    actor_hand: list[DungeonCrawlerCard] = []
    actor_discard: list[DungeonCrawlerCard] = []
    round_stack: list = []
    is_dead: bool = False
    location_on_grid: tuple = None
    targeting_priority: str = "first"

    def model_post_init(self, __context: Any) -> None:
        random.shuffle(self.actor_deck)

    @abstractmethod
    def play_action(self, actors: list[Actor], battle_grid: BattleGrid):
        pass

    def _get_enemy_neighbors(self, actors: list[Actor]) -> list[tuple[int, int]]:
        """Return a list of all adjacent enemy actors.  Here, enemy is defined by
        the actor's class.  This is used to determine which actors are valid targets.
        
        Args:
            actors (list[Actor]): A list of all actors in the battle.
        
        Returns:
            list[Actor]: A list of all adjacent enemy actors."""
        neighbors = [
            (self.location_on_grid[0] - 1, self.location_on_grid[1]),
            (self.location_on_grid[0] + 1, self.location_on_grid[1]),
            (self.location_on_grid[0], self.location_on_grid[1] - 1),
            (self.location_on_grid[0], self.location_on_grid[1] + 1),
        ]

        return [
            actor
            for actor in actors
            if (actor.location_on_grid in neighbors)
            & (actor.is_dead == False)
            & (isinstance(actor, self.__class__) == False)
        ]

    @abstractmethod
    def _replenish_deck(self):
        pass

    def _draw_cards(self):
        """Draw cards from the actor's deck until the actor's hand is full.
        If the deck is empty, shuffle the discard pile and add it to the deck.
        The replenish method differs by enemy and player."""
        cards_to_draw = self.actor_hand_limit - len(self.actor_hand)
        if len(self.actor_deck) < cards_to_draw:
            print("Shuffling discard")
            self._replenish_deck()

        print("Drawing cards")
        for i in range(0, cards_to_draw):
            self.actor_hand.append(self.actor_deck.pop())
        print(f"Actor hand: {[x.name for x in self.actor_hand]}")

    def begin_new_round(self):
        """Right now, beginning a round just draws cards."""
        self._draw_cards()

    def move(
        self, action: DungeonCrawlerAction, actors: list[Actor], battle_grid: BattleGrid
    ):
        """Move the actor.  This is called by the battle controller.  Because the 
        movement logic might change over time, we allow a passthrough where there
        otherwise would be a direct call to the move method."""
        self._move_to_closest(action, actors, battle_grid)

    @abstractmethod
    def _resolve_move_when_adjacent(self, actor: Actor):
        """Differs by monster and player"""
        pass

    def _move_to_closest(
        self, action: DungeonCrawlerAction, actors: list[Actor], battle_grid: BattleGrid
    ):
        """Move the actor to the closest enemy.  If the actor is already adjacent
        to an enemy, this method will call the _resolve_move_when_adjacent method.
        Otherwise, it will find the closest enemy and move towards it.
        
        Args:
            actors (list[Actor]): A list of all actors in the battle.
            battle_grid (BattleGrid): The battle grid, used to determine which
                squares are occupied and which are not.
                
                #TODO The location determination
                is inconsistent between functions.  Sometimes we use a list
                of actors, sometimes we use the grid.  We should standardize."""
        paths = [
            astar(battle_grid, self.location_on_grid, actor.location_on_grid)
            for actor in actors
        ]
        shortest_path = min(paths, key=len)
        # If we're already adjacent to a target, no need to move more
        if shortest_path is None or len(shortest_path) == 1:
            self._resolve_move_when_adjacent(actors)
        # If we can move all the way to the target, do so
        if len(shortest_path) - 1 <= self.actor_movement:
            self.location_on_grid = shortest_path[-1]
        # Otherwise, move as far as possible
        else:
            # This prevents us from moving into a space occupied by another actor
            offset = 0
            while battle_grid[shortest_path[self.actor_movement - offset]] != 0:
                offset += 1
            self.location_on_grid = shortest_path[self.actor_movement - offset]

    def _select_target(
        self, actors: list[Actor]
    ) -> Actor:
        """Select a target from a list of actors.  The target is selected based
        on the actor's targeting priority.  The options are "weakest" (lowest health),
        "strongest" (highest health), and "first"."""
        if self.targeting_priority == "weakest":
            return min(actors, key=lambda actor: actor.actor_current_health)
        elif self.targeting_priority == "strongest":
            return max(actors, key=lambda actor: actor.actor_current_health)
        elif self.targeting_priority == "first":
            return min(actors, key=lambda actor: actor.actor_initiative)
        else:
            raise ValueError(f"Unknown targeting priority {self.targeting_priority}")

    @abstractmethod
    def _execute_attack(self, target: Actor):
        """Attacks differ between monsters and players."""
        pass

    def attack(self, actors: list[Actor]):
        """Execute an attack.  This is called by the battle controller.  Note that
        this may whiff; if no actors are adjacent, the attack will do nothing."""
        target = self._select_target(self._get_enemy_neighbors(actors))
        if target is not None:
            self._execute_attack(target)
