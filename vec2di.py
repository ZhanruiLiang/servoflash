class V2I:
    def __init__(self, (x, y)):
        self.x = int(x)
        self.y = int(y)

    def __add__(self, v):
        return V2I(self.x + v[0], self.y + v[1])

    def __sub__(self, v):
        return V2I(self.x + v[0], self.y + v[1])

    def __div__(self, k):
        return V2I(self.x / k, self.y / k)

    def __mul__(self, k):
        return V2I(self.x * k, self.y * k)

    def __item__(self, i):
        if i == 0:
            return self.x
        else:
            return self.y

    def to_pair(self):
        return (self.x, self.y)
