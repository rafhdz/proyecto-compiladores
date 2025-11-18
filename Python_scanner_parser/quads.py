class Quadruple:
    def __init__(self, op, left, right, res):
        self.op = op
        self.left = left
        self.right = right
        self.res = res

    def __repr__(self):
        return f"({self.op}, {self.left}, {self.right}, {self.res})"

# para poder implementar los cuadruplos y temporales