# Monte Carlo Simulation AI to support Azul Summer Pavilion (and other games)

This project entails two primary components:
- Monte Carlo AI Engine (authored and maintained by [Jen Wadkins](https://github.com/threnjen) and loosely based on MCTS code by [Bosonic Studios](https://ai-boson.github.io/mcts/)
- Azul: Summer Pavilion Game Logic (authored and maintained by [Andrew Herrmann](https://github.com/aherrmann85))
- Minor additional game logic for testing:
  - "Numpy array" 1p testing game
  - Tic Tac Toe 2p testing game


The goal of the Monte Carlo AI Engine is one of portability and reusability. Using simple hooks, any game logice rules can be written to interface with the engine, allowing its reuse across multiple games and with any game logic. The engine does not require knowledge of specific game rules in order to function.

Currently the engine supports up to 2 player games.
