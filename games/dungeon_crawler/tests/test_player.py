from games.dungeon_crawler.player import Player
from games.dungeon_crawler.action import DungeonCrawlerAction
from games.dungeon_crawler.enemy import Enemy
import pytest
from games.dungeon_crawler.actor import Actor


@pytest.fixture
def actors_adjacent_1_0():
    return [
        Enemy(location_on_grid=(2, 0), actor_current_health=6),
        Enemy(location_on_grid=(1, 1), actor_current_health=8),
        Enemy(location_on_grid=(0, 1), actor_current_health=3),
    ]


@pytest.fixture
def player_on_grid_1_0():
    return Player(location_on_grid=(1, 0))


class TestPlayer:
    def test_replenish_deck_empty_discard(self, player_on_grid_1_0: Player):
        player_on_grid_1_0.actor_discard = []
        player_on_grid_1_0.actor_deck = [1, 2, 3]
        player_on_grid_1_0._replenish_deck()
        assert player_on_grid_1_0.actor_deck == [1, 2, 3]

    def test_replenish_deck_nonempty_discard(self, player_on_grid_1_0: Player):
        player_on_grid_1_0.actor_discard = [4, 5, 6]
        player_on_grid_1_0.actor_deck = [1, 2, 3]
        player_on_grid_1_0._replenish_deck()
        assert set(player_on_grid_1_0.actor_deck) == set([4, 5, 6, 1, 2, 3])
        assert player_on_grid_1_0.actor_discard == []
        assert player_on_grid_1_0.actor_deck[:3] == [1, 2, 3]

    def test_replenish_deck_empty_deck(self, player_on_grid_1_0: Player):
        player_on_grid_1_0.actor_discard = [4, 5, 6]
        player_on_grid_1_0.actor_deck = []
        player_on_grid_1_0._replenish_deck()
        assert set(player_on_grid_1_0.actor_deck) == set([4, 5, 6])
        assert player_on_grid_1_0.actor_discard == []

    def test_replenish_deck_empty_both(self, player_on_grid_1_0: Player):
        player_on_grid_1_0.actor_discard = []
        player_on_grid_1_0.actor_deck = []
        player_on_grid_1_0._replenish_deck()
        assert player_on_grid_1_0.actor_deck == []
        assert player_on_grid_1_0.actor_discard == []

    def test_replenish_deck_nonempty_both(self, player_on_grid_1_0: Player):
        player_on_grid_1_0.actor_discard = [4, 5, 6]
        player_on_grid_1_0.actor_deck = [1, 2, 3]
        player_on_grid_1_0._replenish_deck()
        assert set(player_on_grid_1_0.actor_deck) == set([4, 5, 6, 1, 2, 3])
        assert player_on_grid_1_0.actor_discard == []

    def test_get_neighbors(self, player_on_grid_1_0: Player):
        actors = [
            Enemy(location_on_grid=(0, 1)),
            Enemy(location_on_grid=(1, 1)),
            Enemy(location_on_grid=(2, 0)),
            Enemy(location_on_grid=(2, 2)),
        ]
        neighbors = player_on_grid_1_0._get_enemy_neighbors(actors)
        assert len(neighbors) == 2
        assert neighbors[0].location_on_grid == (1, 1)
        assert neighbors[1].location_on_grid == (2, 0)

    def test_get_neighbors_no_neighbors(self, player_on_grid_1_0: Player):
        actors = [
            Enemy(location_on_grid=(0, 1)),
            Enemy(location_on_grid=(2, 2)),
        ]
        neighbors = player_on_grid_1_0._get_enemy_neighbors(actors)
        assert neighbors == []

    def test_get_neighbors_no_actors(self, player_on_grid_1_0: Player):
        actors = []
        neighbors = player_on_grid_1_0._get_enemy_neighbors(actors)
        assert neighbors == []

    def test_get_neighbors_no_enemies(self, player_on_grid_1_0: Player):
        actors = [
            Player(location_on_grid=(0, 1)),
            Player(location_on_grid=(2, 2)),
        ]
        neighbors = player_on_grid_1_0._get_enemy_neighbors(actors)
        assert neighbors == []

    def test_select_target_first(
        self, player_on_grid_1_0: Player, actors_adjacent_1_0: list[Actor]
    ):
        player_on_grid_1_0.targeting_priority = "first"
        target = player_on_grid_1_0._select_target(actors_adjacent_1_0)
        assert target.location_on_grid == (2, 0)

    def test_select_target_weakest(
        self, player_on_grid_1_0: Player, actors_adjacent_1_0: list[Actor]
    ):
        player_on_grid_1_0.targeting_priority = "weakest"
        target = player_on_grid_1_0._select_target(actors_adjacent_1_0)
        assert target.location_on_grid == (0, 1)

    def test_select_target_weakest_same_health(
        self, player_on_grid_1_0: Player, actors_adjacent_1_0: list[Actor]
    ):
        player_on_grid_1_0.targeting_priority = "weakest"
        actors_adjacent_1_0[1].actor_current_health = actors_adjacent_1_0[
            2
        ].actor_current_health
        target = player_on_grid_1_0._select_target(actors_adjacent_1_0)
        assert target.location_on_grid == (1, 1)

    def test_select_target_strongest(
        self, player_on_grid_1_0: Player, actors_adjacent_1_0: list[Actor]
    ):
        player_on_grid_1_0.targeting_priority = "strongest"
        target = player_on_grid_1_0._select_target(actors_adjacent_1_0)
        assert target.location_on_grid == (1, 1)

    def test_select_target_strongest_same_health(
        self, player_on_grid_1_0: Player, actors_adjacent_1_0: list[Actor]
    ):
        player_on_grid_1_0.targeting_priority = "strongest"
        actors_adjacent_1_0[0].actor_current_health = actors_adjacent_1_0[
            1
        ].actor_current_health
        target = player_on_grid_1_0._select_target(actors_adjacent_1_0)
        assert target.location_on_grid == (2, 0)

    def test_execute_attack(self, player_on_grid_1_0: Player):
        target = Enemy(location_on_grid=(1, 1), actor_current_health=8)
        player_on_grid_1_0.actor_attack = 3
        player_on_grid_1_0._execute_attack(target)
        assert target.actor_current_health == 5
        assert target.is_dead == False

    def test_execute_attack_negative(self, player_on_grid_1_0: Player):
        target = Enemy(location_on_grid=(1, 1), actor_current_health=8)
        player_on_grid_1_0.actor_attack = 10
        player_on_grid_1_0._execute_attack(target)
        assert target.actor_current_health == 0
        assert target.is_dead == True

    def test_execute_attack_zero(self, player_on_grid_1_0: Player):
        target = Enemy(location_on_grid=(1, 1), actor_current_health=8)
        player_on_grid_1_0.actor_attack = 8
        player_on_grid_1_0._execute_attack(target)
        assert target.actor_current_health == 0
        assert target.is_dead == True

    def test_attack_single(self, player_on_grid_1_0: Player):
        target = Enemy(location_on_grid=(1, 1), actor_current_health=8)
        actors = [target]
        player_on_grid_1_0.actor_attack = 3
        player_on_grid_1_0.targeting_priority = "weakest"
        player_on_grid_1_0.attack(actors)
        assert target.actor_current_health == 5
        assert target.is_dead == False

    def test_attack_multiple_adjacent(self, player_on_grid_1_0: Player):
        target1 = Enemy(location_on_grid=(1, 1), actor_current_health=8)
        target2 = Enemy(location_on_grid=(2, 0), actor_current_health=6)
        actors = [target1, target2]
        player_on_grid_1_0.actor_attack = 3
        player_on_grid_1_0.targeting_priority = "first"
        player_on_grid_1_0.attack(actors)
        assert target1.actor_current_health == 5
        assert target1.is_dead == False
        assert target2.actor_current_health == 6
        assert target2.is_dead == False

    def test_attack_multiple_nonadjacent(self, player_on_grid_1_0: Player):
        target1 = Enemy(location_on_grid=(2, 2), actor_current_health=6)
        target2 = Enemy(location_on_grid=(1, 1), actor_current_health=8)
        actors = [target1, target2]
        player_on_grid_1_0.actor_attack = 3
        player_on_grid_1_0.attack(actors)
        assert target1.actor_current_health == 6
        assert target1.is_dead == False
        assert target2.actor_current_health == 5
        assert target2.is_dead == False

    def test_attack_multiple_adjacent_weakest(self, player_on_grid_1_0: Player):
        target1 = Enemy(location_on_grid=(1, 1), actor_current_health=8)
        target2 = Enemy(location_on_grid=(2, 0), actor_current_health=6)
        actors = [target1, target2]
        player_on_grid_1_0.actor_attack = 3
        player_on_grid_1_0.targeting_priority = "weakest"
        player_on_grid_1_0.attack(actors)
        assert target1.actor_current_health == 8
        assert target1.is_dead == False
        assert target2.actor_current_health == 3
        assert target2.is_dead == False

    def test_attack_multiple_adjacent_strongest(self, player_on_grid_1_0: Player):
        target1 = Enemy(location_on_grid=(1, 1), actor_current_health=8)
        target2 = Enemy(location_on_grid=(2, 0), actor_current_health=6)
        actors = [target1, target2]
        player_on_grid_1_0.actor_attack = 3
        player_on_grid_1_0.targeting_priority = "strongest"
        player_on_grid_1_0.attack(actors)
        assert target1.actor_current_health == 5
        assert target1.is_dead == False
        assert target2.actor_current_health == 6
        assert target2.is_dead == False

    def test_attack_multiple_adjacent_first(self, player_on_grid_1_0: Player):
        target1 = Enemy(location_on_grid=(1, 1), actor_current_health=8)
        target2 = Enemy(location_on_grid=(2, 0), actor_current_health=6)
        actors = [target1, target2]
        player_on_grid_1_0.actor_attack = 3
        player_on_grid_1_0.targeting_priority = "first"
        player_on_grid_1_0.attack(actors)
        assert target1.actor_current_health == 5
        assert target1.is_dead == False
        assert target2.actor_current_health == 6
        assert target2.is_dead == False
