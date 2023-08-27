import numpy as np
import pandas as pd
import multiprocessing as mp
import time
from datetime import datetime

from engine.game_engine import GameEngine
from itertools import repeat


class GameMultiprocessor:
    def __init__(self, game_name, sims, player_count, verbose, num_games, decay):
        self.game_name = game_name
        self.sims = sims
        self.player_count = player_count
        self.verbose = verbose
        self.num_games = num_games
        self.decay = decay
        self.timestamp = datetime.now().strftime("%m%d%Y_%H%M%S")

    def playout_simulations(self):
        time_start = time.time()

        pools = mp.cpu_count()
        print(f"Number of cpu cores available: {pools}")
        processes = 32
        print(f"Number of processes: {processes}")
        self.end = self.num_games
        self.block = int(np.ceil(self.end / processes))
        self.values = np.arange(0, self.end, self.block)
        pool = mp.Pool(processes=processes)
        scores = pool.starmap(GameMultiprocessor.process_block, zip(repeat(self), self.values))
        pool.close()
        time_end = round(time.time() - time_start, 3)
        time_per_game = round(time_end / self.num_games, 2)
        print(
            f"Series took {time_end} seconds for {self.num_games} games with {self.sims} simulations each. Average {time_per_game} per game."
        )

        all_games = []
        for game_set in scores:
            for game, data in game_set.items():
                this_game = {}
                this_game["Game"] = game
                for key, value in data["scores"].items():
                    this_game[f"Player {key}"] = value
                for item in data["turn_log"]:
                    this_game[f"T{item['Turn']} P{item['Player']}"] = item["Action"]

                all_games.append(this_game)

        master_game_log = pd.DataFrame(all_games)
        master_game_log[f"starting_sims"] = self.sims
        master_game_log[f"decay_method"] = self.decay
        master_game_log[f"game_time"] = time_per_game

        master_game_log.to_csv(
            f"logs/{self.game_name}_turn_log_{self.sims}_sims_{self.num_games}_games_{self.decay}_{self.timestamp}.csv",
            index=False,
        )

    def process_block(self, values):
        block_games = {}

        end = values + self.block

        if end > self.num_games:
            end = self.num_games

        for games in range(values, end):
            block_games[str(games)] = {}
            game = GameEngine(
                game_name=self.game_name,
                sims=self.sims,
                player_count=self.player_count,
                verbose=self.verbose,
                decay=self.decay,
            )
            game.play_game_by_turns(self.sims)

            block_games[str(games)]["scores"] = game.get_game_scores()
            block_games[str(games)]["turn_log"] = game.game_log

        return block_games
