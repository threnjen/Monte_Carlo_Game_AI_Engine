class Enemy:
    def __init_subclass__(cls) -> None:
        pass

    def create_enemy_deck(self):
        self.enemy_deck = ["S1", "S2", "S3", "Move", "Attack"]
        self.enemy_deck *= 3
        print(self.enemy_deck)


if __name__ == "__main__":
    enemy = Enemy()
    enemy.create_enemy_deck()
