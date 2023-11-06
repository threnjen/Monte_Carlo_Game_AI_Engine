class Enemy:
    def __init__(self) -> None:
        self.enemy_deck = self.create_enemy_deck()
        print(self.enemy_deck)

    def create_enemy_deck(self):
        enemy_deck = ["S1", "S2", "S3", "Move", "Attack"]
        enemy_deck *= 3
        return enemy_deck


if __name__ == "__main__":
    enemy = Enemy()
    enemy.create_enemy_deck()
