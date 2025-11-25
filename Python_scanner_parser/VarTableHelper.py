from FuncDir import FuncDir  

class VarTableHelper:
    def __init__(self, funcdir):
        self.funcdir = funcdir

    def add_var(self, name, var_type):
        scope = self.funcdir.current_scope()
        addr = self.funcdir.memory.alloc_var(scope, var_type)
        self.funcdir.add_variable(name, var_type, addr)

    def lookup(self, name):
        return self.funcdir.lookup_variable(name)