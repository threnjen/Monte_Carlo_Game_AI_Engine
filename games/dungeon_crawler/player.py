class Player:
    def __init_subclass__(cls) -> None:
        pass

    def create_deck(self):
        self.player_deck = ["Attack", "Attack", "Attack", "Move", "Move"]
        max_deck_size = 12
        while len(self.player_deck) < max_deck_size:
            pass
