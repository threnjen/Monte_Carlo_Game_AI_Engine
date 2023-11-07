from card import *

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
    DefenseCard(name="Base_Defense", modifier=0),
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
ENEMY_DECK = [
    AttackCard(name="Base_Attack", modifier=0),
    AttackCard(name="Base_Attack", modifier=0),
    AttackCard(name="Base_Attack", modifier=0),
    MoveCard(name="Base_Move", modifier=0),
    MoveCard(name="Base_Move", modifier=0),
    MoveCard(name="Base_Move", modifier=0),
    SpecialCard(name="Special_1", modifier=0),
    SpecialCard(name="Special_1", modifier=0),
    SpecialCard(name="Special_1", modifier=0),
    SpecialCard(name="Special_2", modifier=0),
    SpecialCard(name="Special_2", modifier=0),
    SpecialCard(name="Special_2", modifier=0),
    SpecialCard(name="Special_3", modifier=0),
    SpecialCard(name="Special_3", modifier=0),
    SpecialCard(name="Special_3", modifier=0),
]
