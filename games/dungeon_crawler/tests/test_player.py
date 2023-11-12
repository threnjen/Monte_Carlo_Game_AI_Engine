from games.dungeon_crawler.player import Player
from games.dungeon_crawler.action import DungeonCrawlerAction
from games.dungeon_crawler.enemy import Enemy
import pytest
from games.dungeon_crawler.actor import Actor


class TestPlayer:
    @classmethod
    def setup_class(cls):
        cls.player = Player(location_on_grid=(1, 0))
        cls.actors_adjacent_1_0 = [
            Enemy(location_on_grid=(2,0), actor_current_health=6),
            Enemy(location_on_grid=(1,1), actor_current_health=8),
            Enemy(location_on_grid=(0,1), actor_current_health=3)
            ]

    def test_replenish_deck_empty_discard(self):
        self.player.actor_discard = []
        self.player.actor_deck = [1, 2, 3]
        self.player._replenish_deck()
        assert self.player.actor_deck == [1, 2, 3]

    def test_replenish_deck_nonempty_discard(self):
        self.player.actor_discard = [4, 5, 6]
        self.player.actor_deck = [1, 2, 3]
        self.player._replenish_deck()
        assert set(self.player.actor_deck) == set([4, 5, 6, 1, 2, 3])
        assert self.player.actor_discard == []
        assert self.player.actor_deck[:3] == [1, 2, 3]

    def test_replenish_deck_empty_deck(self):
        self.player.actor_discard = [4, 5, 6]
        self.player.actor_deck = []
        self.player._replenish_deck()
        assert set(self.player.actor_deck) == set([4, 5, 6])
        assert self.player.actor_discard == []

    def test_replenish_deck_empty_both(self):
        self.player.actor_discard = []
        self.player.actor_deck = []
        self.player._replenish_deck()
        assert self.player.actor_deck == []
        assert self.player.actor_discard == []

    def test_replenish_deck_nonempty_both(self):
        self.player.actor_discard = [4, 5, 6]
        self.player.actor_deck = [1, 2, 3]
        self.player._replenish_deck()
        assert set(self.player.actor_deck) == set([4, 5, 6, 1, 2, 3])
        assert self.player.actor_discard == []

    def test_get_neighbors(self):
        actors = [
            Enemy(location_on_grid=(0, 1)),
            Enemy(location_on_grid=(1, 1)),
            Enemy(location_on_grid=(2, 0)),
            Enemy(location_on_grid=(2, 2)),
        ]
        neighbors = self.player._get_enemy_neighbors(actors)
        assert len(neighbors) == 2
        assert neighbors[0].location_on_grid == (1, 1)
        assert neighbors[1].location_on_grid == (2, 0)

    def test_get_neighbors_no_neighbors(self):
        actors = [
            Enemy(location_on_grid=(0, 1)),
            Enemy(location_on_grid=(2, 2)),
        ]
        neighbors = self.player._get_enemy_neighbors(actors)
        assert neighbors == []

    def test_get_neighbors_no_actors(self):
        actors = []
        neighbors = self.player._get_enemy_neighbors(actors)
        assert neighbors == []

    def test_get_neighbors_no_enemies(self):
        actors = [
            Player(location_on_grid=(0, 1)),
            Player(location_on_grid=(2, 2)),
        ]
        neighbors = self.player._get_enemy_neighbors(actors)
        assert neighbors == []

    def test_select_target_first(self):
        self.player.targeting_priority = "first"
        target = self.player._select_target(self.actors_adjacent_1_0)
        assert target.location_on_grid == (2,0)

    def test_select_target_weakest(self):
        self.player.targeting_priority = "weakest"
        target = self.player._select_target(self.actors_adjacent_1_0)
        assert target.location_on_grid == (0,1)

    def test_select_target_weakest_same_health(self):
        self.player.targeting_priority = "weakest"
        self.actors_adjacent_1_0[1].actor_current_health = self.actors_adjacent_1_0[2].actor_current_health
        target = self.player._select_target(self.actors_adjacent_1_0)
        assert target.location_on_grid == (1,1)

    def test_select_target_strongest(self):
        self.player.targeting_priority = "strongest"
        target = self.player._select_target(self.actors_adjacent_1_0)
        assert target.location_on_grid == (1,1)

    def test_select_target_strongest_same_health(self):
        self.player.targeting_priority = "strongest"
        self.actors_adjacent_1_0[0].actor_current_health = self.actors_adjacent_1_0[1].actor_current_health
        target = self.player._select_target(self.actors_adjacent_1_0)
        assert target.location_on_grid == (2,0)

    def test_execute_attack(self):
        target = Enemy(location_on_grid=(1,1), actor_current_health=8)
        self.player.actor_attack = 3
        self.player._execute_attack(target)
        assert target.actor_current_health == 5
        assert target.is_dead == False

    def test_execute_attack_negative(self):
        target = Enemy(location_on_grid=(1,1), actor_current_health=8)
        self.player.actor_attack = 10
        self.player._execute_attack(target)
        assert target.actor_current_health == 0
        assert target.is_dead == True

    def test_execute_attack_zero(self):
        target = Enemy(location_on_grid=(1,1), actor_current_health=8)
        self.player.actor_attack = 8
        self.player._execute_attack(target)
        assert target.actor_current_health == 0
        assert target.is_dead == True

    def test_attack_single(self):
        target = Enemy(location_on_grid=(1,1), actor_current_health=8)
        actors = [target]
        self.player.actor_attack = 3
        self.player.targeting_priority = "weakest"
        self.player.attack(actors)
        assert target.actor_current_health == 5
        assert target.is_dead == False

    def test_attack_multiple_adjacent(self):
        target1 = Enemy(location_on_grid=(1,1), actor_current_health=8)
        target2 = Enemy(location_on_grid=(2,0), actor_current_health=6)
        actors = [target1, target2]
        self.player.actor_attack = 3
        self.player.targeting_priority = "first"
        self.player.attack( actors)
        assert target1.actor_current_health == 5
        assert target1.is_dead == False
        assert target2.actor_current_health == 6
        assert target2.is_dead == False

    def test_attack_multiple_nonadjacent(self):
        target1 = Enemy(location_on_grid=(2,2), actor_current_health=6)
        target2 = Enemy(location_on_grid=(1,1), actor_current_health=8)
        actors = [target1, target2]
        self.player.actor_attack = 3
        self.player.attack( actors)
        assert target1.actor_current_health == 6
        assert target1.is_dead == False
        assert target2.actor_current_health == 5
        assert target2.is_dead == False

    def test_attack_multiple_adjacent_weakest(self):
        target1 = Enemy(location_on_grid=(1,1), actor_current_health=8)
        target2 = Enemy(location_on_grid=(2,0), actor_current_health=6)
        actors = [target1, target2]
        self.player.actor_attack = 3
        self.player.targeting_priority = "weakest"
        self.player.attack( actors)
        assert target1.actor_current_health == 8
        assert target1.is_dead == False
        assert target2.actor_current_health == 3
        assert target2.is_dead == False

    def test_attack_multiple_adjacent_strongest(self):
        target1 = Enemy(location_on_grid=(1,1), actor_current_health=8)
        target2 = Enemy(location_on_grid=(2,0), actor_current_health=6)
        actors = [target1, target2]
        self.player.actor_attack = 3
        self.player.targeting_priority = "strongest"
        self.player.attack(actors)
        assert target1.actor_current_health == 5
        assert target1.is_dead == False
        assert target2.actor_current_health == 6
        assert target2.is_dead == False

    def test_attack_multiple_adjacent_first(self):
        target1 = Enemy(location_on_grid=(1,1), actor_current_health=8)
        target2 = Enemy(location_on_grid=(2,0), actor_current_health=6)
        actors = [target1, target2]
        self.player.actor_attack = 3
        self.player.targeting_priority = "first"
        self.player.attack( actors)
        assert target1.actor_current_health == 5
        assert target1.is_dead == False
        assert target2.actor_current_health == 6
        assert target2.is_dead == False


