from VarInfo import VarInfo

class FuncDir:
    def __init__(self):
        self.functions = {}
        self.current_function = "global"
        self.functions["global"] = {
            "ret": "void",
            "vars": {},
            "params": [],
        }
        self.memory = None  # es asignado por el listener

    def current_scope(self):
        return "glob" if self.current_function == "global" else "loc"

    def add_function(self, name, ret_type):
        self.current_function = name
        self.functions[name] = {
            "ret": ret_type,
            "vars": {},
            "params": [],
        }

    def set_global(self):
        self.current_function = "global"

    def add_variable(self, name, var_type, address):
        self.functions[self.current_function]["vars"][name] = VarInfo(
            name, var_type, address
        )

    def lookup_variable(self, name):
        if name in self.functions[self.current_function]["vars"]:
            return self.functions[self.current_function]["vars"][name]
        if name in self.functions["global"]["vars"]:
            return self.functions["global"]["vars"][name]
        raise Exception(f"Variable '{name}' no declarada")