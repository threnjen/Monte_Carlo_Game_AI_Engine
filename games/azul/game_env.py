from games.game_components.game import GameEnvironment
from .player import AzulPlayer
from .azul import AzulGame
from random import choice

class AzulGameEnvironment(GameEnvironment):
    game: AzulGame
    players: dict[int, AzulPlayer]
    first_player_num: None
    current_player_num: int = 0

    @property
    def current_player(self) -> AzulPlayer:
        return self.players[self.current_player_num]

    @property
    def player_count(self) -> int:
        return len(self.players)

    def play_out_game(self):
        while not self.game.is_game_over():
            self.start_round()
            self._play_phase_one()
            self._play_phase_two()


    def _play_phase_one(self):
        while not self.game.factory.is_factory_empty():
            actions = self.current_player.get_available_actions(self.game)
            chosen_action = self.current_player.choose_action(actions)
            new_tiles, first_player_ind = self.game.factory.update_game_with_action(chosen_action, self.game.wild_color)
            if first_player_ind:
                self.first_player_num = self.current_player_num
            self.current_player.player_tile_supply += new_tiles
            self.current_player_num = (self.current_player_num + 1) % self.player_count

    def _play_phase_two(self):
        while any([not player.done_placing for player in self.players.values()]):
            while not self.current_player.done_placing:
                actions = self.current_player.get_available_actions(self.game)
                chosen_action = self.current_player.choose_action(actions)
                self.current_player.update_game_with_action(chosen_action, self.game)
            self.current_player_num = (self.current_player_num + 1) % self.player_count

    def start_round(self):
        if self.first_player_num is None:
            self.first_player_num = choice(self.players.keys())
        self.current_player_num = self.first_player_num
        self.game.start_round()
        for player in self.players.values():
            player.start_round_for_player()
