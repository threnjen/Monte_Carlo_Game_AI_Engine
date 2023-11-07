from pydantic import BaseModel


class DungeonCrawlerCard(BaseModel):
    type: str
    modifier: int


class AttackCard(DungeonCrawlerCard):
    name: str
    type: str = "attack"
    modifier: int


class DefenseCard(DungeonCrawlerCard):
    name: str
    type: str = "defense"
    modifier: int


class MoveCard(DungeonCrawlerCard):
    name: str
    type: str = "move"
    modifier: int


class RecoverCard(DungeonCrawlerCard):
    name: str
    type: str = "recover"
    modifier: int


class SpecialCard(DungeonCrawlerCard):
    name: str
    type: str = "special"
    modifier: int
