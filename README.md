# Monte Carlo AI Engine
## With Azul: Summer Pavilion Game Logic

This project entails these components:
- Monte Carlo AI Engine (authored and maintained by [Jen Wadkins](https://github.com/threnjen))
- Azul: Summer Pavilion Game Logic (authored and maintained by [Andrew Herrmann](https://github.com/aherrmann85))
- Otrio Game Logic (authored and maintained by [Jen Wadkins](https://github.com/threnjen))
- Additional game logic for testing:
  - "Numpy array" 1p testing game
  - Tic Tac Toe 2p testing game

Monte Carlo Tree Search is an AI method that allows an AI to make a game move based on an exploration of potential future game states. Unlike a fully exhaustive tree search, which would require the AI to play out every possible game permutation from a given game state, Monte Carlo Tree Search will explore promising game states until either a time or simulation count has been reached. At this point it will return the best possible move found within the alloted search time. This AI method allows great flexibility in tuning opponent difficulty. If given enough simulations, the MCTS will inevitably optimize each turn. If constrained to very few simulations, it can be effectively handicapped to a lower skill level.

The goal of the Monte Carlo AI Engine is one of portability and reusability. Using simple game-agnostic hooks, any game logic rules can interface with the engine. The engine does not require knowledge of any game rules in order to function, and can operate with any number of players. All or some of the players can be AI, and all AI players will play using MCTS. Optional game reports can be saved to disk for further analysis.

For use with the Monte Carlo AI Engine, a game logic requires only four specific hooks:

> Hook #1 requires a list with two indices in the format [[list of legal actions], active player ID]. The engine does not care about the contents of the list of legal actions, and will return a list item in exactly the same format as it is presented.

> Hook #2 is an update function that returns a move to the game logic from the list received in Hook #1, as well as returning the active player ID.

> Hook #3 asks if the game is over and receives a True/False boolean.

> Hook #4 gets the game score and requires a dictionary in the format of {playerID : score}. The playerID in the scores must match the ID used for Hooks #1 and #2.

The game logic must manage the correct player turns and the game flow, so that it is always prepared to send a list of available actions along with the correct player to take those actions. The engine has no checks on the accuracy of the player ID or the actions presented.

Special thanks to [Bosonic Studios](https://ai-boson.github.io/mcts/), whose MCTS starter code was a pivotal learning tool.

**Future work**: Save games AI plays against itself to build a training catalog for Neural Net



