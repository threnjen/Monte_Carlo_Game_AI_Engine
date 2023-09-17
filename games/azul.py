# %%
from __future__ import annotations
from random import choice
from random import randrange
from random import sample
from itertools import combinations
from .gui_tryout import display_stuff
from collections import Counter


def print_dict(print_dictionary: dict[str, int]) -> str:
    """Prints a dictionary.  Only really used for debugging.

    Args:
        print_dictionary (dict): To print

    Returns:
        str: Printed dictionary
    """
    return "\n".join([f"{key}: {value}" for key, value in print_dictionary.items()])





class ScoreBoard:
    """Master scoreboard.  Only tracks player points and the round number."""

    def __init__(self, player_colors: int):
        """
        Not an interesting object

        Args:
            player_colors (dict): color/score pairs.  Scores are 5 to start.
        """
        self.player_colors = player_colors
        self.round_number = 0

    def increment_round(self):
        """Adds one to the round number"""
        self.round_number += 1

    def increase_player_score(self, player: int, points: int):
        """Adds the points to the player color

        Args:
            player (str): Player color
            points (int): Points added (or removed)
        """
        self.player_colors[player] += points


class Player:
    starting_points = 5
    max_tile_reserve = 4
    player_colors = ["brown", "white", "black", "gray"]

    def __init__(self, player_ind: int, first_player: bool = False):
        """Player, which is a surprisingly simple object so far.  The idea is that most actions
        will be controled outside of the player, since we can't pass objects in.

        Args:
            color (str): Player color
            first_player (bool, optional): Whether this is the first player. Defaults to False.
        """
        self.color = self.player_colors[player_ind]
        self.first_player = first_player
        self.player_tile_supply = MASTER_TILE_DICTIONARY.copy()
        self.player_board = PlayerBoard(player_ind)
        self.player_score = Player.starting_points
        self.tile_count = 0
        self.legal_moves = {}
        self.bonus_earned = 0
        self.done_placing = False

    # I'm not sure it's valuable to have the player turn occur here rather than the game, but
    # I could see it being useful for passing control around.
    def change_player_supply(self, added_tiles: dict, method: str = "add"):
        """Alters the amount of tiles in the player supply.

        Args:
            added_tiles (dict): Tiles to alter.
            method (optional, str): Whether we should add or remove tiles.  Default 'add'.
        """
        for color in added_tiles.keys():
            if method == "add":
                self.player_tile_supply[color] += added_tiles[color]
            elif method == "remove":
                self.player_tile_supply[color] -= added_tiles[color]

    def choose_tiles_to_reserve(
        self, tiles_to_choose: int = 4, act_count: int = 0
    ) -> dict:
        """We can only reserve four tiles, so this picks them.

        Args:
            tiles_to_choose (int, optional): [description]. Defaults to 4.
            act_count (int, optional): [description]. Defaults to 0.

        Returns:
            [type]: [description]
        """
        tiles = []
        for color, cnt in self.player_tile_supply.items():
            if cnt:
                tiles.extend([color] * cnt)
        choice_list = list(set(combinations(tiles, tiles_to_choose)))
        legal_moves = {}
        for option in choice_list:
            reserve_dict = {}
            for j in option:
                if j not in reserve_dict.keys():
                    reserve_dict[j] = 0
                reserve_dict[j] += 1
            legal_moves[act_count] = reserve_dict
            act_count += 1
        return legal_moves

    def get_tile_count(self):
        return sum([tile_count for tile_count in self.player_tile_supply.values()])

    def check_tile_supply(self, color: str, wilds_used: int, tiles_needed: int) -> bool:
        """Confirms we have the correct number of tiles to cover a position.
        Used to determine legal moves.

        Args:
            color (str): Tile color
            wilds_used (int): Number of wilds we can use
            tiles_needed (int): Number of tiles needed

        Returns:
            bool: Player has sufficient tiles for position
        """
        return self.player_tile_supply[color] + wilds_used >= tiles_needed


class Game:
    """The game class will handle all aspects of the game.  All other objects will
    be instantiated in here.
    """

    tiles_per_factory = 4
    tiles_per_color = 22
    total_rounds = 6
    supply_max = 10
    reserve_max = 4
    wild_list = {1: "purple", 2: "green", 3: "orange", 4: "yellow", 5: "blue", 6: "red"}
    factory_req = {1: 9, 2: 5, 3: 7, 4: 9}
    first_player_cost = -2

    def __init__(self, player_count: int):
        """Builds the game from the player count.
        Args:
            player_count (int): Player count for this game.
        """
        self.factory = Factory(Game.factory_req[player_count])
        self.supply = Supply()
        self.players = {i: Player(i) for i in range(player_count)}
        self.bag = Bag(
            132,
            {color: Game.tiles_per_color for color in MASTER_TILE_DICTIONARY.keys()},
        )
        self.tower = Tower()
        self.current_round = 1
        self.current_player_num = None
        self.first_player = None
        self.end_round = True
        self.place_tile_phase = False
        self.wild_color = None
        self.select_starting_player(player_count)
        self._state = None
        self.phase = 1
        self.start_round()
        self.game_over = False
        self.save_state()
        self.name = "Azul"

    def select_starting_player(self, player_count: int):
        """Called once at the beginning of the game."""
        self.first_player = randrange(0, player_count)
        self.players[self.first_player].first_player = True

    def fill_supply(self):
        """Fills the supply with tiles (up to 10).  Called at the beginning
        of the game, beginning of the round, and after a player is done placing tiles
        in phase two."""

        supply_count = self.supply.get_tile_count()
        self.supply.fill_supply(
            self.bag.randomly_choose_tiles(Game.supply_max - supply_count, self.tower)
        )

    def get_legal_actions(self, rollout: bool = False):
        """Called before every player_count turn.  Depends on the board state and current player.
        This shouldn't alter the game state except at the beginning of a round"""
        curr_player = self.players[self.current_player_num]
        if self.phase == 1:
            # Legal actions include taking tiles from the factory displays
            curr_player.legal_moves = self.factory.get_legal_actions(self.wild_color)
            return curr_player.legal_moves, self.current_player_num
        elif curr_player.bonus_earned and self.supply.get_tile_count():
            # Legal actions incluide taking tiles from the supply
            curr_player.legal_moves = self.supply.get_legal_actions()
            return curr_player.legal_moves.keys(), self.current_player_num
        else:
            # Legal actions include placing tiles on the player board or ending the turn
            player_tiles = curr_player.player_tile_supply
            curr_board = curr_player.player_board
            act_count, legal_moves = curr_board.get_legal_actions(
                player_tiles, self.wild_color
            )
            tile_count = sum([cnt for cnt in player_tiles.values()])
            if legal_moves and tile_count > 5:
                # To simplify for the bot, we don't allow a player to reserve tiles (and
                # end the turn) until they have five or fewer left or no other option
                pass
            else:
                # If there are four or fewer, there's no reserve choice to be made
                if tile_count <= 4:
                    legal_moves[act_count] = player_tiles
                else:
                    # Otherwise, we have to make a choice
                    legal_moves = {
                        **legal_moves,
                        **curr_player.choose_tiles_to_reserve(4, act_count),
                    }

            curr_player.legal_moves = legal_moves

            return list(legal_moves.keys()), self.current_player_num

    def move_reserves_to_player_supply(self):
        for player in self.players.values():
            player.change_player_supply(player.player_board.reserved_tiles)
            player.player_board.reserved_tiles = {}

    def start_round(self):
        """Begins a round (including the first one).

        Args:
            round (int): Round number
            wild_color (str): Wild color for the round.
        """
        self.fill_supply()
        self.wild_color = Game.wild_list[self.current_round]
        for display in self.factory.factory_displays.values():
            tile_dict = self.bag.randomly_choose_tiles(
                Game.tiles_per_factory, self.tower
            )
            display.add_tiles_to_container(tile_dict)

        self.move_reserves_to_player_supply()
        self.phase = 1
        self.current_player_num = self.first_player
        for player in self.players.values():
            player.done_placing = False
        self.factory.center.reset_first_player()
        self.save_state()

    def update_game_with_action(self, action, player_num: int = -1):
        """Updates the game with a player action.  Note that an action can be
        multiple types depending on the action.  This is probably really bad.

        Args:
            action (var): Player action.
        """

        curr_player = self.players[self.current_player_num]
        sel_action = curr_player.legal_moves[action]
        if self.phase == 1:
            # If we're in phase one, the action is to take tiles from
            # a factory.  If there are tiles left after that, the next player
            # takes a turn.  Otherwise, the next player is whoever has the first
            # player token and we move to phase 2
            gained_tiles, first_player_change = self.factory.take_tiles(
                sel_action, self.wild_color
            )
            if first_player_change:
                self.first_player = self.current_player_num
                curr_player.player_score += self.first_player_cost
                curr_player.first_player = True
            curr_player.change_player_supply(gained_tiles)
            if self.factory.get_legal_actions(self.wild_color):
                self.current_player_num = (self.current_player_num + 1) % self.players
            else:
                self.phase = 2
                self.current_player_num = self.first_player

        elif curr_player.bonus_earned and self.supply.get_tile_count():
            # If the player earned a bonus, the action is to take a tile from the
            # supply. We decrement the earned bonus by 1, add the tile to the player
            # supply, remove the tile from the global supply, and refresh the supply
            # tile count
            # Here, the sel_action is a tile color
            if self.supply.get_tile_count():
                curr_player.change_player_supply(
                    {self.supply._tile_positions.pop(action): 1}
                )
                curr_player.bonus_earned -= 1
            else:
                curr_player.bonus_earned = 0

            # self.supply.refresh_positions()
        elif type(sel_action) is dict:
            # This is trickier.  The player can choose to stop placing tiles at any time.
            # If they do so, the action is a dictionary of tiles they would like to reserve
            # We check for that filetype, reserve the tiles, decrease player points (if
            # appropriate) reset the player tiles (reserves go to the player board), and
            # mark the player is done placing tiles.  This last step ensures that next time they
            # have a turn, it will be round 1 (see get_legal_moves)
            curr_player.player_board.reserved_tiles = sel_action
            for tile, tile_count in curr_player.player_tile_supply.items():
                try:
                    self.tower.tile_dictionary[tile] += tile_count - sel_action[tile]
                except KeyError:
                    self.tower.tile_dictionary[tile] += tile_count
            curr_player.player_score += min(
                self.reserve_max - curr_player.get_tile_count(), 0
            )
            curr_player.player_tile_supply = MASTER_TILE_DICTIONARY.copy()
            curr_player.done_placing = True
            self.fill_supply()
            self.current_player_num = (self.current_player_num + 1) % self.players
        else:
            # If they didn't stop placing tiles, they will place one here.
            # Remove the tiles from the player supply (using negatives),
            # add the tiles back to the tower, place the tiles, and collect
            # the bonuses and points.
            used_tiles = {}
            used_tiles[sel_action[1]] = sel_action[3]
            if sel_action[1] != self.wild_color:
                used_tiles[self.wild_color] = sel_action[4]

            curr_player.change_player_supply(used_tiles, method="remove")
            # This is a little clunky (reusing the dictionary), but seems cleaner
            # than creating a new one
            used_tiles[curr_player.legal_moves[action][1]] -= 1
            # We subtract one because one of the tiles stays on the player board.
            self.tower.add_tiles_to_container(used_tiles)
            # We pass the action array to the player board to add a tile and receive points
            # and a possible bonus back
            bonus_tile_count, points = curr_player.player_board.add_tile_to_star(
                curr_player.legal_moves[action]
            )
            curr_player.bonus_earned = bonus_tile_count
            curr_player.player_score += points

        self.save_state()
        if all([player.done_placing for player in self.players.values()]):
            self.current_round += 1
            if self.current_round > self.total_rounds:
                self.move_reserves_to_player_supply()
                for player in self.players.values():
                    player.player_score += -player.get_tile_count()
                self.game_over = True
                print(f"Game result: {print_dict(self.get_game_scores())}")
            else:
                self.start_round()

    def is_game_over(self) -> bool:
        return self.game_over

    def get_game_scores(self) -> dict[int, int]:
        return {
            player_num: player.player_score
            for player_num, player in self.players.items()
        }

    def save_state(self):
        "Called at the end of every player_count action"
        self._state = f"Phase: {self.phase}\n"
        self._state += f"Current_player:  {self.current_player_num}\n"
        self._state += (
            f"First player available: {self.factory.center._first_player_avail}\n"
        )
        self._state += f"First player for next round: {self.first_player}\n"
        for key, disp in self.factory.factory_displays.items():
            self._state += f"Factory display {key} tiles:\n"
            self._state += f"{print_dict(disp.get_available_tiles(self.wild_color))}\n"
        self._state += "Center tiles: \n"
        self._state += (
            f"{print_dict(self.factory.center.get_available_tiles(self.wild_color))}\n"
        )
        self._state += "Supply tiles: \n"
        self._state += f"{self.supply._tile_positions}"
        for player_number, player in self.players.items():
            self._state += f"Player {player_number} score: {player.player_score}\n"
            self._state += f"Player {player_number} tiles:\n"
            self._state += f"{print_dict(player.player_tile_supply)}\n"
            for color, star in player.player_board.stars.items():
                if color == "all":
                    self._state += (
                        f"Player {player_number} {color} star avail colors:\n"
                    )
                    self._state += f"{print_dict(star.colors_allowed)}\n"
                self._state += f"Player {player_number} {color} star open positions: \n"
                self._state += f"{print_dict(star.get_open_positions())}\n"

    def prep_display(self):
        factory_dict = {}
        for ind, disp in self.factory.factory_displays.items():
            factory_dict[ind] = disp.tile_dictionary
        factory_dict[-1] = self.factory.center.tile_dictionary
        supply_dict = Counter(self.supply._tile_positions)
        player_dict = {}
        stars = {}
        for ind, player in self.players.items():
            player_dict[ind] = player.player_tile_supply
            stars[ind] = {}
            for star_ind, star in player.player_board.stars.items():
                stars[ind].update({star_ind: star.tile_positions})
        score_dict = {
            player_num: player.player_score
            for player_num, player in self.players.items()
        }

        action = display_stuff(
            factory_dict,
            supply_dict,
            player_dict,
            stars,
            self.players[self.current_player_num].legal_moves,
            score_dict,
        )
        return action

    def play_game(self):
        """Plays the game (in the case where we are not using a bot)"""
        while not self.is_game_over():
            self.get_legal_actions()
            # print(self._state)

            for key, value in self.players[self.current_player_num].legal_moves.items():
                print(f"{value}:  enter {key}")
            action = self.prep_display()
            # action = int(input("Choose an action"))
            self.update_game_with_action(action)


# %%
test = Game(2)
test.play_game()

# %%
