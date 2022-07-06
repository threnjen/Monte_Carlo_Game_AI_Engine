import pytest

class TestGameEngine:

    def test_engine(self, engine):
        assert engine.simulations==10
        assert engine.player_count==3
        assert engine.verbose==True

    def test_legal_actions(self, engine):

        actions, player = engine.get_legal_actions(policy=False)
        assert actions==[(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (2, 0), (2, 1), (2, 2), (2, 3), (2, 4), (3, 0), (3, 1), (3, 2), (3, 3), (3, 4), (4, 0), (4, 1), (4, 2), (4, 3), (4, 4)]
        assert player==0

    def test_game_over(self, engine):
        game_over = engine.is_game_over()
        assert game_over == False

    def test_update_game(self, engine):
        engine.update_game((0, 0), 0)
        actions, player  = engine.get_legal_actions(policy=False)
        assert actions==[(0, 1), (0, 2), (0, 3), (0, 4), (1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (2, 0), (2, 1), (2, 2), (2, 3), (2, 4), (3, 0), (3, 1), (3, 2), (3, 3), (3, 4), (4, 0), (4, 1), (4, 2), (4, 3), (4, 4)]
        assert player==0
        pass

    def test_game_result(self):
        pass

    def test_play_out_game(self, engine):
        engine.play_game_byturns()
        game_over = engine.is_game_over()
        assert game_over == True