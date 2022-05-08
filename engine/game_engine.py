# this file is the custom monte carlo framework for our AI to plug into

import numpy as np
import pandas as pd
from random import randint
import importlib

from monte_carlo_engine import MonteCarloEngine

class GameEngine():
    
    def __init__(self, game, players=2, verbose=False):
        """
        Initializes game.

        The following hooks are required in the Game __init__ file:
        game init must accept players argument (int)
        self._state: is used to display whatever information you want to print to the player (ex. game board in tic tac toe)
        self.scores: dictionary holds the player scores and should be initialized with the player ID and base score (0 in many games)
        self.name: a lowercase string with no spaces to define the game in log files
        """      
        # import game module based on argument  
        game_module = importlib.import_module(game)
        self.game = game_module.Game(players)
        #self.state = self.game._state
        self.player_count = players
        self.verbose = verbose

        self.game_log = pd.DataFrame(columns=['Turn', 'Actions', 'Player', 'Action', 'Score', 'Simulations'])
        
    # get_legal_actions(self, rollout=False):
        """
        Hook #1
        Get currently available actions and active player to take an action from the list

        Requires a list with two indices:
        0: list of legal actions
        1: active player ID

        Format [[list of legal actions], active player ID]

        The Monte Carlo does not care about the contents of the list of legal actions, and will return
        a list item in exactly the same format it presents in the list

        The game logic must manage the correct player turns. The Monte Carlo engine will assign the
        next legal action to the player passed, with no safety checks.

        Returns:
            [list]: List of: list of legal actions and active player ID
        """        

    #def update_game(self, action, player):
        """
        Hook #2
        Send action choice and player to game

        After selecting an item from the list of legal actions (see Hook #1),
        Sends the item back to the game logic. Item is sent back in exactly
        the same format as received in the list of legal actions.

        Also returns active player ID for action

        Args:
            action (list item): selected item from list of legal actions
            player (int): player number
        """        
        #return self.game.update_game(action, player)

    #def is_game_over(self):
        """
        Hook #3
        Checks if game has ended

        Requires only True or False

        Returns:
            [True/False]: True/False if game is over
        """        
        #return self.game.is_game_over()

    #def game_result(self):
        """
        Hook #4
        Retrieves game score

        Must be a dictionary in format {playerID: Score}
        Where playerID matches IDs sent with get_legal_actions

        Returns:
            [dict]: dictionary in format playerID: score
        """        
        #return self.game.game_result()

    def play_game_byturns(self, simulations):
        """
        Intializes Monte Carlo engine
        Will play a single game until game over condition is met

        Args:
            simulations (int): Number of simulations to run per turn
        """        
        # toggle to print to file
        #sys.stdout = open('logs/'+self.game.name+'_'+str(self.player_count)+'players_'+str(simulations)+'sims_'+str(randint(1,1000000))+'.txt', "w")
        print("Players: "+str(self.player_count))
        print("Sims: "+str(simulations))

        self.turn = 0 # Set the initial turn as 0
        
        current_player=self.game.get_legal_actions()[1] # Get starting player

        self.montecarlo = MonteCarloEngine(current_player) # initiate the monte carlo engine
        self.current_node = self.montecarlo.root # set first node as monte carlo root

        self.sims_this_turn = simulations # set number of simulations

        while not self.game.is_game_over():

            #turn_log = pd.DataFrame(columns=['Turn', 'Actions', 'Player', 'Action', 'Score', 'Simulations'])
            turn_log = {}

            self.turn += 1 # increments the game turn
            turn_log['Turn']=self.turn

            actions=self.game.get_legal_actions()[0]
            turn_log['Actions']=actions
            
            # Beginning of game repoprting:
            print("\n\nTurn "+str(self.turn))
            print('Current board state: ')
            print(self.game._state) # prints the game board            
            print("Game gets "+str(self.sims_this_turn)+' simulations for this turn.')
            print("Player's turn: Player "+str(current_player)) #whose turn is it?

            # Toggle the following block for heavy reporting
            if self.verbose:
                try:
                   print("Entry state") 
                   print(self.current_node.depth, self.current_node.node_action, self.current_node.player_owner, self.current_node)
                   selected_node = self.current_node.best_child(print_weights=True)
                except: pass

            # Run the monte carlo engine for this turn. This accesses the meat of the engine right here!
            # returns a chosen action to implement and the new active node
            self.current_node = self.montecarlo.play_turn(self.sims_this_turn, self.game, current_player, self.current_node)
            best_action = self.current_node.node_action # gets action of the returned node
            print("Move: "+str(best_action))

            self.game.update_game(best_action, current_player) # updates the true game state with the MC simmed action
            turn_log['Simulations'] = self.sims_this_turn
            turn_log['Player']= current_player
            turn_log['Action']= str(best_action)
            self.scores = self.game.game_result() # get game scores
            turn_log['Score']=self.scores[current_player]

            current_player = self.game.get_legal_actions()[1] # update current player

            self.game_log = self.game_log.append(turn_log, ignore_index=True)

            # Add simulation decay if desired. Uncomment choices below for two types of simulation decay.
            #self.sims_this_turn = int(np.ceil(self.sims_this_turn*.9)) # simulation decay of .9 each round
            #self.sims_this_turn = int(np.ceil(self.simulations/(self.turn))) # simulation decay to absolute simulations/turn each round

        # Game over report
        print("\n\n\nGame over. Game took "+str(self.turn)+" turns.")
        self.scores = self.game.game_result() # get game scores
        print(self.game._state) # print final board
        print(self.scores) # print final scores

        # toggle to print to file
        #sys.stdout.close()

        #self.game_log.to_pickle('logs/'+self.game.name+'_game_log_'+str(randint(1,1000000))+'.pkl')
        #first_action_list=[]

        #for i in range(self.simulations):

        #    self.action = self.turn_engine.play_turn(1, self.game, self.player) 
        #    first_action_list.append(tuple(self.action))         
        
        #df = pd.DataFrame(first_action_list)
        #df['pairs'] = df.apply(lambda x: (str(x[0])+", "+str(x[1])), axis=1)
        #df.to_pickle('first_action_list'+str(game_label)+'.pkl')



