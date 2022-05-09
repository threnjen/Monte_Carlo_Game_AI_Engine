# this file is the custom monte carlo framework for our AI to plug into

import numpy as np
import pandas as pd
from random import randint
import importlib
import sys

from engine.monte_carlo_engine import MonteCarloEngine


class GameEngine():

    def __init__(self, game, sims=100, players=2, verbose=False):
        """
        Initializes game.

        The following hooks are required in the Game __init__ file:
        game init must accept players argument (int)
        self._state: is used to display whatever information you want to print to the player (ex. game board in tic tac toe)
        self.scores: dictionary holds the player scores and should be initialized with the player ID and base score (0 in many games)
        self.name: a lowercase string with no spaces to define the game in log files
        """
        self.verbose = verbose
        # import game module based on argument
        game_module = importlib.import_module(f'.{game}', package='games')
        instance = getattr(game_module, 'SimpleArrayGame')
        self.game = instance(players)
        self.player_count = players
        self.simulations = sims
        self.turn = 0  # Set the initial turn as 0
        self.game_log = pd.DataFrame(columns=[
            'Turn', 'Actions', 'Player', 'Action', 'Score', 'Simulations'
        ])
    
    def get_legal_actions(self, policy=False):
        """
        Hook #1
        Get currently available actions and active player to take an action from the list

        Requires return of a list with two indices:
        0: list of legal actions
        1: active player ID

        Format [[list of legal actions], active player ID]

        The engine does not care about the contents of the list of legal actions, and will return
        a list item in exactly the same format it is passed. The game logic must manage the correct player turns. The Monte Carlo engine will assign the
        next legal action to the player passed, with no safety checks.

        Returns:
            [list]: List of: list of legal actions and active player ID
        """

        return self.game.get_legal_actions(policy)

    def is_game_over(self):
        """
        Hook #3
        Checks if game has ended

        Requires only True or False

        Returns:
            [True/False]: True/False if game is over
        """
        return self.game.is_game_over()

    def update_game(self, action, player):
        """
        Hook #2
        Sends action choice and player to game

        After selecting an item from the list of legal actions (see Hook #1),
        Sends the item back to the game logic. Item is sent back in exactly
        the same format as received in the list of legal actions.

        Also returns active player ID for action

        Args:
            action (list item): selected item from list of legal actions
            player (int): player number
        """
        return self.game.update_game(action, player)

    def game_result(self):
        """
        Hook #4
        Retrieves game score

        Must be a dictionary in format {playerID: Score}
        Where playerID matches IDs sent with get_legal_actions

        Returns:
            [dict]: dictionary in format playerID: score
        """
        return self.game.game_result()

    
    def draw_board(self):

        return self.game.draw_board()


    def update_turn_log(self, best_action, sims_this_turn, current_player):
        self.turn_log['Turn'] = self.turn
        self.turn_log['Simulations'] = sims_this_turn
        self.turn_log['Player'] = current_player
        self.turn_log['Action'] = str(best_action)
        scores = self.game_result()
        self.turn_log['Score'] = scores[current_player]

    
    def play_game_byturns(self):
        """
        Intializes Monte Carlo engine
        Will play a single game until game over condition is met
        """
        #if self.verbose:
            #sys.stdout = open(f'logs/{self.game.name}_{self.player_count}players_{self.simulations}sims_{randint(1,1000000)}.txt', "w")
        print(f"Players: {self.player_count}, Sims: {self.simulations}")

        current_player = self.get_legal_actions(policy=False)[1]  # Get starting player

        self.montecarlo = MonteCarloEngine(current_player, self.verbose)  # initialize the monte carlo engine
        current_node = self.montecarlo.root  # set first node as monte carlo root

        sims_this_turn = self.simulations  # set number of simulations; re-assigned here for decay usage

        while not self.is_game_over():

            self.turn_log = {}
            self.turn += 1  # increments the game turn
            actions = self.get_legal_actions()[0]
            self.turn_log['Actions'] = actions
            current_player = self.get_legal_actions()[1]  # update current player

            # Beginning of game reporting:
            print(f"\n\nTurn {self.turn}\nCurrent board state: {self.draw_board()}\nGame gets {sims_this_turn} simulations for this turn. Player {current_player}'s turn.")

            if self.verbose:
                try:
                    print("Entry state")
                    print(current_node.depth,
                          current_node.node_action,
                          current_node.player_owner, current_node)
                    selected_node = current_node.best_child(
                        print_weights=True)
                except:
                    pass

            # Run the monte carlo engine for this turn. This accesses the meat of the engine right here!
            # returns a chosen action to implement and the new active node
            current_node = self.montecarlo.play_turn(
                sims_this_turn, self.game, current_player,
                current_node)
            best_action = current_node.node_action  # gets action of the returned node
            print("Move: " + str(best_action))

            self.update_game(
                best_action, current_player)  # updates the true game state with the MC simmed action
            self.update_turn_log(best_action, sims_this_turn, current_player)

            self.game_log = self.game_log.append(self.turn_log, ignore_index=True)

            # Add simulation decay if desired. Uncomment choices below for two types of simulation decay.
            sims_this_turn = int(np.ceil(sims_this_turn*.9)) # simulation decay of .9 each round
            #sims_this_turn = int(np.ceil(self.simulations/(self.turn))) # simulation decay to absolute simulations/turn each round

        # Game over report
        print(f"\n\n\nGame over. Game took {self.turn} turns.\n{self.draw_board()}\n{self.game_result()}")

        #if self.verbose:
            #sys.stdout.close()

        #self.game_log.to_pickle('logs/'+self.game.name+'_game_log_'+str(randint(1,1000000))+'.pkl')
        
        #first_action_list=[]

        #for i in range(self.simulations):

        #    self.action = self.turn_engine.play_turn(1, self.game, self.player)
        #    first_action_list.append(tuple(self.action))

        #df = pd.DataFrame(first_action_list)
        #df['pairs'] = df.apply(lambda x: (str(x[0])+", "+str(x[1])), axis=1)
        #df.to_pickle('first_action_list'+str(game_label)+'.pkl')

        

        

        

       
