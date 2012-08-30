class V2I(tuple):
    def __init__(self, (x, y)):
        tuple.__init__(self, (x, y))

    def __add__(self, v):
        return V2I((self[0] + v[0], self[1] + v[1]))

    def __sub__(self, v):
        return V2I((self[0] - v[0], self[1] - v[1]))

    def __div__(self, k):
        return V2I((self[0] / k, self[1] / k))

    def __mul__(self, k):
        return V2I((self[0] * k, self[1] * k))

    def __item__(self, i):
        if i == 0:
            return self[0]
        else:
            return self[1]
