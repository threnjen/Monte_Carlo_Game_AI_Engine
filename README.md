# Monte Carlo AI Engine
## With Azul: Summer Pavilion Game Logic

This project entails these components:
- Monte Carlo AI Engine (authored and maintained by [Jen Wadkins](https://github.com/threnjen))
- (In Progress) Azul: Summer Pavilion Game Logic (authored and maintained by [Andrew Herrmann](https://github.com/aherrmann85))
- Otrio Game Logic (authored and maintained by [Jen Wadkins](https://github.com/threnjen))
- (In Progress) Sagrada Game Logic (authored and maintained by [Jen Wadkins](https://github.com/threnjen))
- Additional game logic for testing:
  - "Numpy array" 1p testing game
  - Tic Tac Toe 2p testing game
  - Connect Four 2p testing game

Monte Carlo Tree Search is an AI method that allows an AI to make a game move based on an exploration of potential future game states. Unlike a fully exhaustive tree search, which would require the AI to play out every possible game permutation from a given game state, Monte Carlo Tree Search will explore promising game states until either a time or simulation count has been reached. At this point it will return the best possible move found within the alloted search time. This AI method allows great flexibility in tuning opponent difficulty. If given enough simulations, the MCTS will inevitably optimize each turn. If constrained to very few simulations, it can be effectively handicapped to a lower skill level. As a method it is agnostic to game rules and requires no hard-coding of game decisions.

The goal of the Monte Carlo AI Engine is one of portability and reusability. Using simple game-agnostic hooks, any game logic rules can interface with the engine. The engine does not require knowledge of any game rules in order to function, and can operate with any number of player_count. All or some of the player_count can be AI, and all AI player_count will play using MCTS. Optional game reports can be saved to disk for further analysis.

For use with the Monte Carlo AI Engine, a game logic requires six lightweight hooks:

> Hook #1 *get_current_player* Has no arguments. It must return an integer for the current player number. Game will use this integer when receiving actions for this player, so it must be both sent and received in the same format in which the game logic utilizes it.

> Hook #2 *get_available_actions* must return a list in the format [list of legal actions]. The engine does not care about the contents of the list of legal actions, and use the list item in exactly the same format as it is presented.
get_available_actions must accept a boolean argument of special_policy, but use of this parameter in the game logic is optional.

> Hook #3 *update_game_with_action* accepts two arguments. The first is a list item from the get_available_actions list, and the second is a player integer. It must use these arguments to record a move for the game for the correct player.

> Hook #4 *is_game_over* returns a True/False boolean for if the game is over.

> Hook #5 *get_game_scores* gets the game score and returns a dictionary in the format of {playerID : score}. The playerID in the scores must match the ID used for Hooks #1 and #2.

> Hook #6 *draw_board* the game engine must draw the board state in a minimal GUI representation

The game logic must manage the correct player turns and the game flow, so that it is always prepared to send a list of available actions along with the correct player to take those actions. The engine has no checks on the accuracy of the player ID or the actions presented.

Special thanks to [Bosonic Studios](https://ai-boson.github.io/mcts/), whose MCTS starter code was a pivotal learning tool.

**Future work**: Save games AI plays against itself to build a training catalog for Neural Net



