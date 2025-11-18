class TempManager:
    def __init__(self, memory):
        self.memory = memory
        self.counter = 0

    def new_temp(self, vtype):
        # Esto genera un temporal y su dirección virtual real
        addr = self.memory.alloc_temp(vtype)
        name = f"t{self.counter}"
        self.counter += 1
        return name, addr