from games.dungeon_crawler.player import Player
from games.dungeon_crawler.enemy import Enemy
import pytest
from games.dungeon_crawler.actor import Actor

@pytest.fixture
def enemy_on_grid_1_0():
    return Enemy(location_on_grid=(1, 0), targeting_priority="first")


class TestEnemy:
    def test_replenish_deck_nonempty_discard(self, enemy_on_grid_1_0: Enemy):
        enemy_on_grid_1_0.actor_discard = [4, 5, 6]
        enemy_on_grid_1_0.actor_deck = [1, 2, 3]
        enemy_on_grid_1_0._replenish_deck()
        print(enemy_on_grid_1_0.actor_deck)
        assert set(enemy_on_grid_1_0.actor_deck) == set([4, 5, 6, 1, 2, 3])
        assert enemy_on_grid_1_0.actor_discard == []

    def test_get_neighbors(self, enemy_on_grid_1_0: Enemy):
        actors = [
            Player(location_on_grid=(0, 1)),
            Player(location_on_grid=(1, 1)),
            Player(location_on_grid=(2, 0)),
            Player(location_on_grid=(2, 2)),
        ]
        neighbors = enemy_on_grid_1_0._get_enemy_neighbors(actors)
        assert len(neighbors) == 2
        assert neighbors[0].location_on_grid == (1, 1)
        assert neighbors[1].location_on_grid == (2, 0)

    def test_get_neighbors_no_enemies(self, enemy_on_grid_1_0: Enemy):
        actors = [
            Enemy(location_on_grid=(0, 1)),
            Enemy(location_on_grid=(2, 2)),
        ]
        neighbors = enemy_on_grid_1_0._get_enemy_neighbors(actors)
        assert neighbors == []

    def test_execute_attack(self, enemy_on_grid_1_0: Enemy):
        target = Player(location_on_grid=(1, 1))
        target_cards = len(target.actor_discard)
        enemy_on_grid_1_0._execute_attack(target)
        target_cards_after = len(target.actor_discard)
        assert target_cards_after == target_cards + 1
