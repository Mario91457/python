from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class Vec2:
    x: int
    y: int