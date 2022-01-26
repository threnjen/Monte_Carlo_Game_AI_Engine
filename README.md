# Monte Carlo Simulation AI to support Azul Summer Pavilion (and other games)

This project entails these components:
- Monte Carlo AI Engine (authored and maintained by [Jen Wadkins](https://github.com/threnjen))
- Azul: Summer Pavilion Game Logic (authored and maintained by [Andrew Herrmann](https://github.com/aherrmann85))
- Otrio Game Logic (authored and maintained by [Jen Wadkins](https://github.com/threnjen))
- Additional game logic for testing:
  - "Numpy array" 1p testing game
  - Tic Tac Toe 2p testing game


The goal of the Monte Carlo AI Engine is one of portability and reusability. Using simple game-agnostic hooks, any game logic rules can interface with the engine. The engine does not require knowledge of specific game rules in order to function, and can operate with any number of players.

For use with the Monte Carlo AI Engine, a game logic requires only four specific hooks:

> - Hook #1: 
  Requires a list with two indices:
       0: list of legal actions
       1: active player ID
  In the format [[list of legal actions], active player ID]
      The Monte Carlo does not care about the contents of the list of legal actions, and will return
        a list item in exactly the same format it presents in the list

  The game logic must manage the correct player turns. The Monte Carlo engine will assign the
   next legal action to the player passed, with no safety checks.

       

Special thanks to [Bosonic Studios](https://ai-boson.github.io/mcts/), whose MCTS starter code was a pivotal teaching tool.



