class TempManager:
    def __init__(self, memory):
        self.memory = memory
        self.counter = 0
        self.addr_to_name = {}

    def new_temp(self, vtype):
        # Genera un temporal y guarda un alias legible para debug
        addr = self.memory.alloc_temp(vtype)
        name = f"t{self.counter}"
        self.counter += 1
        self.addr_to_name[addr] = name
        return name, addr
