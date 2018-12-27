from math import cos, sin, sqrt, radians


class Vector2D:
    def __init__(self, *args):
        if args.__len__() == 2:
            self.x, self.y = args[0], args[1]
        elif args.__len__() == 1:
            self.x, self.y = args[0]
        else:
            self.x, self.y = 0.0, 0.0

    def __add__(self, other):
        if len(other) == len(self):
            return self.__class__(*(a + b for a, b in zip(self, other)))
        else:
            raise TypeError

    def __sub__(self, other):
        if len(other) == len(self):
            return self.__class__(*(a - b for a, b in zip(self, other)))
        else:
            raise TypeError

    def __mul__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            return self.__class__(self.x * other, self.y * other)
        else:
            raise TypeError

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            return self.__class__(self.x / other, self.y / other)
        else:
            raise TypeError

    def __neg__(self):
        return self.__class__(-self.x, -self.y)

    def __len__(self):
        return 2

    def __getitem__(self, key):
        return (self.x, self.y)[key]

    def __repr__(self):
        return "{} ({}, {})".format(self.__class__.__name__, self.x, self.y)

    def length(self):
        return sqrt(self.x ** 2 + self.y ** 2)

    def normalize(self):
        length = self.length()
        return self.__class__(self.x / length, self.y / length)

    def rotate(self, theta):
        theta = radians(theta)
        dc, ds = cos(theta), sin(theta)
        x, y = dc * self.x - ds * self.y, ds * self.x + dc * self.y
        return self.__class__(x, y)

    def dot(self, other):
        return self.x * other.x + self.y * other.y

    def cross(self, other):
        return self.x * other.y - self.y * other.x

    def orthogonal(self):
        return self.__class__(self.x, -self.y)
