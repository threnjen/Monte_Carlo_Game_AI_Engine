import random


class Player:
    def __init__(self):
        self.avail_start_cards = ["Attack", "Move", "Recover", "Defend"]
        self.avail_start_cards *= 3
        self.player_deck = self.create_deck()
        print(self.player_deck)

    def create_deck(self):
        player_deck = ["Attack", "Attack", "Attack", "Move", "Move"]
        max_deck_size = 12
        while len(player_deck) < max_deck_size:
            pop_card = self.add_start_card_to_deck()
            if player_deck.count(pop_card) < 5:
                player_deck.append(pop_card)
        return player_deck

    def add_start_card_to_deck(self):
        pop_card = random.choice(self.avail_start_cards)
        return pop_card


if __name__ == "__main__":
    player = Player()
