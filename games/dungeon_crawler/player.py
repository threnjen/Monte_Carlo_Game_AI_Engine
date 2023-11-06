class Player:
    def __init__(self):
        self.player_deck = self.create_deck()

    def create_deck(self):
        player_deck = ["Attack", "Attack", "Attack", "Move", "Move"]
        max_deck_size = 12
        while len(player_deck) < max_deck_size:
            pass
        return player_deck

    def avail_start_cards(self):
        avail_start_cards = ["Attack", "Move", "Recover"]
