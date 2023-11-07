# Notes:

## Actors
The way I've laid it out below, it seems like a general `Actor` class could be the starting point for both player and monster

### Player needs:
- `get_available_actions`
    - Currently just the cards
    - Later requires the directions, which will interact with the grid
- Container to hold round actions (with the ability to pop)
- Health
- Max health
- Initiative
- Death indicator/method
- Discard deck
- Owner (human or computer)

### Monster needs:
- Method to move closer to player on grid
    - Requires a shortest path algorithm
        - Should this always move horizontal first and then vertical, or be random?  Probably random
    - Need logic for when the monster is already adjacent to a player and pulls a move
    - May way to replace "adjacent" with "cells away from" to allow range later (in other words, don't hardcode the 1? or do monsters always want to get closer?)
- Method to attack adjacent player (does this live in the battle?)
- Method to select random action (card)
- Deck
- Max health
- Death indicator/method
- Health
- Initiative
- Special list
- Type
- Discard deck
- Owner (human or computer)
- Species (rename later) (ghost, zombie, etc.)


### Battle Grid needs:
- method to empty cells adjacent to actor (this may belong in the actor?)
- method to get targets adjacent to actor (this may belong in the actor?)
- Way to update actor movement (this makes me question if the grid is necessary)

### Battle needs:
- Game flow logic

