import pytest
from engine import game_engine



class TestGameEngine:
    def test_engine(self, engine: game_engine.GameEngine):
        assert engine.number_of_sims == 10
        assert engine.player_count == 3
        assert engine.verbose == True

    def test_legal_actions(self, engine: game_engine.GameEngine):

        actions, player = engine.get_available_actions(special_policy=False)
        assert actions == [
            (0, 0),
            (0, 1),
            (0, 2),
            (0, 3),
            (0, 4),
            (1, 0),
            (1, 1),
            (1, 2),
            (1, 3),
            (1, 4),
            (2, 0),
            (2, 1),
            (2, 2),
            (2, 3),
            (2, 4),
            (3, 0),
            (3, 1),
            (3, 2),
            (3, 3),
            (3, 4),
            (4, 0),
            (4, 1),
            (4, 2),
            (4, 3),
            (4, 4),
        ]
        assert player == 0

    def test_game_over(self, engine: game_engine.GameEngine):
        game_over = engine.is_game_over()
        assert game_over == False

    def test_update_game_with_action(self, engine: game_engine.GameEngine):
        engine.update_game_with_action((0, 0), 0)
        actions, player = engine.get_available_actions(special_policy=False)
        assert actions == [
            (0, 1),
            (0, 2),
            (0, 3),
            (0, 4),
            (1, 0),
            (1, 1),
            (1, 2),
            (1, 3),
            (1, 4),
            (2, 0),
            (2, 1),
            (2, 2),
            (2, 3),
            (2, 4),
            (3, 0),
            (3, 1),
            (3, 2),
            (3, 3),
            (3, 4),
            (4, 0),
            (4, 1),
            (4, 2),
            (4, 3),
            (4, 4),
        ]
        assert player == 0
        pass

    def test_get_game_scores(self):
        pass

    def test_play_out_game(self, engine: game_engine.GameEngine):
        engine.play_game_by_turns(sims=500)
        game_over = engine.is_game_over()
        assert game_over == True
