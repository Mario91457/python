from math import hypot

class Vector2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    @property
    def magnitude(self):
        return hypot(self.x, self.y)

    def __add__(self, other):
        if isinstance(other, Vector2):
            return Vector2(self.x + other.x, self.y + other.y)
        return NotImplemented

    __radd__ = __add__

    def __sub__(self, other):
        if isinstance(other, Vector2):
            return Vector2(self.x - other.x, self.y - other.y)
        return NotImplemented

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return Vector2(self.x * other, self.y * other)
        return NotImplemented

    __rmul__ = __mul__

    def dot(self, other):
        return self.x * other.x + self.y * other.y
    
    def normalized(self):
        mag = self.magnitude
        if mag == 0:
            return Vector2(0, 0)
        return Vector2(self.x / mag, self.y / mag)

    def __neg__(self):
        return Vector2(-self.x, -self.y)
