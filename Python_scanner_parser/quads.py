class Quadruple:
    def __init__(self, op, left, right, res):
        self.op = op
        self.left = left
        self.right = right
        self.res = res

    def __repr__(self):
        return f"({self.op}, {self.left}, {self.right}, {self.res})"


class TempManager:
    def __init__(self):
        self.counter = 0

    def new_temp(self):
        name = f"t{self.counter}"
        self.counter += 1
        return name
    
# para poder implementar los cuadruplos y temporales