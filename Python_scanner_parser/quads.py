class Quadruple:
    def __init__(self, op, left, right, res):
        self.op = op # entero: opcode
        self.left = left # direcciones virtuales
        self.right = right
        self.res = res

    def __repr__(self):
        return f"({self.op}, {self.left}, {self.right}, {self.res})"

# para poder implementar los cuadruplos y temporales