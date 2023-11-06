from pydantic import BaseModel

class DungeonCrawlerCard(BaseModel):
    type: str
    modifier: int

class AttackCard(DungeonCrawlerCard):
    type: str = 'attack'
    modifier: int

class DefenseCard(DungeonCrawlerCard):
    type: str = 'defense'
    modifier: int

class MoveCard(DungeonCrawlerCard):
    type: str = 'move'
    modifier: int

class RecoverCard(DungeonCrawlerCard):
    type: str = 'recover'
    modifier: int

class SpecialCard(DungeonCrawlerCard):
    type: str = 'special'
    modifier: int