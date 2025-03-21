from dataclasses import dataclass
from typing import List


@dataclass
class Box:
    x: int
    y: int
    width: int
    height: int


@dataclass
class Strategy:
    boxes: List[Box]
    score: int 