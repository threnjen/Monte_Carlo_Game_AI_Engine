from .card import *

BASE_ROUND_ACTIONS = 3
BASE_PLAYER_HAND = 6
BASE_PLAYER_MAX_HEALTH = 3
BASE_PLAYER_ATTACK = 1
BASE_PLAYER_DEFENSE = 1
BASE_PLAYER_RECOVER = 1
BASE_PLAYER_MOVEMENT = 1
BASE_PLAYER_INITIATIVE = 50
BASE_PLAYER_DECK = [
    AttackCard(name="Base_Attack", modifier=0),
    AttackCard(name="Base_Attack", modifier=0),
    AttackCard(name="Base_Attack", modifier=0),
    AttackCard(name="Base_Attack", modifier=0),
    AttackCard(name="Base_Attack", modifier=0),
    MoveCard(name="Base_Move", modifier=0),
    MoveCard(name="Base_Move", modifier=0),
    MoveCard(name="Base_Move", modifier=0),
    MoveCard(name="Base_Move", modifier=0),
    DefenseCard(name="Base_Defense", modifier=0),
    RecoverCard(name="Base_Recover", modifier=0),
    RecoverCard(name="Base_Recover", modifier=0),
]
BASE_ENEMY_MAX_HEALTH = 5
BASE_ENEMY_ATTACK = 1
BASE_ENEMY_DEFENSE = 1
BASE_ENEMY_RECOVER = 1
BASE_ENEMY_MOVEMENT = 1
BASE_ENEMY_INITIATIVE = 49
SAMPLE_ENEMY_SPECIALS = {
    "special_1": {"type": "move", "modifier": 2},
    "special_2": {"type": "attack", "modifier": 2},
    "special_3": {"type": "defense", "modifier": 2},
}
BASE_ENEMY_DECK = [
    AttackCard(name="Base_Attack", modifier=0),
    AttackCard(name="Base_Attack", modifier=0),
    AttackCard(name="Base_Attack", modifier=0),
    MoveCard(name="Base_Move", modifier=0),
    MoveCard(name="Base_Move", modifier=0),
    MoveCard(name="Base_Move", modifier=0),
]
SPECIAL_CARD_TYPE = {"move": MoveCard, "defense": DefenseCard, "attack": AttackCard, "special": SpecialCard}
