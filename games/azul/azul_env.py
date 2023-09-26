from typing import Any
from games.game_components.game import Game
from .player import AzulPlayer
from .azul import AzulGame
from random import choice


class AzulGameEnvironment(Game):
    player_count: int
    players: dict[int, AzulPlayer] = None
    game: AzulGame = None
    first_player_num: int = None
    current_player_num: int = 0

    def model_post_init(self, __context: Any) -> None:
        if self.game is None:
            self.game = AzulGame(player_count=self.player_count)
        if self.players is None:
            self.players = {
                player_num: AzulPlayer(player_number=player_num)
                for player_num in range(self.player_count)
            }
        if self.first_player_num is None:
            self.first_player_num = choice(list(self.players.keys()))

    @property
    def current_player(self) -> AzulPlayer:
        return self.players[self.current_player_num]

    def draw_board(self):
        pass

    def get_available_actions(self, special_policy: bool = False) -> list:
        return self.current_player.get_available_actions(self.game)

    def update_game_with_action(self, action: str, player: int):
        self.current_player.update_game_with_action(action, self.game)

    def get_game_scores(self) -> dict[int, int]:
        return {
            player_num: player.player_score
            for player_num, player in self.players.items()
        }

    def get_game_state(self) -> tuple:
        return self

    def is_game_over(self) -> bool:
        return self.game.is_game_over()

    def get_current_player(self) -> int:
        return self.current_player_num

    def play_out_game(self):
        while not self.game.is_game_over():
            self.start_round()
            self._play_phase_one()
            self._play_phase_two()

    def _play_phase_one(self):
        while not self.game.factory.is_factory_empty():
            actions = self.current_player.get_available_actions(self.game)
            chosen_action = self.current_player.choose_action(actions)
            new_tiles, first_player_ind = self.game.factory.update_game_with_action(
                chosen_action, self.game.wild_color
            )
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
        self.current_player_num = self.first_player_num
        self.game.start_round()
        for player in self.players.values():
            player.start_round_for_player()


test = AzulGameEnvironment(player_count=2)
with open("games/azul/test.json", "w") as f:
    f.write(test.model_dump_json())