# Monte Carlo Simulation AI to support Azul Summer Pavilion (and other games)

This project entails these components:
- Monte Carlo AI Engine (authored and maintained by [Jen Wadkins](https://github.com/threnjen) and loosely originated/learned from MCTS code by [Bosonic Studios](https://ai-boson.github.io/mcts/))
- Azul: Summer Pavilion Game Logic (authored and maintained by [Andrew Herrmann](https://github.com/aherrmann85))
- Minor additional game logic for testing:
  - "Numpy array" 1p testing game
  - Tic Tac Toe 2p testing game


The goal of the Monte Carlo AI Engine is one of portability and reusability. Using simple game-agnostic hooks, any game logic rules can interface with the engine, allowing its reuse across multiple games. The engine does not require knowledge of specific game rules in order to function.

Currently the engine supports up to 2 player games.
