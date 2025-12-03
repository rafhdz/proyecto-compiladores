from VarInfo import VarInfo
from semantics import SemanticError

class FuncDir:
    def __init__(self):
        self.functions = {}
        self.current_function = "global"
        self.functions["global"] = {
            "ret": "void",
            "vars": {},
            "params": [],
            "start": None,
            "return_addr": None,
            "has_return": False,
        }
        self.memory = None  # es asignado por el listener

    def current_scope(self):
        # Regresa el prefijo esperado por la tabla de memoria virtual
        return "glob" if self.current_function == "global" else "loc"

    def add_function(self, name, ret_type):
        # Declara una nueva función y reserva espacio para su retorno si no es void
        if name in self.functions:
            raise SemanticError(f"Función '{name}' ya declarada")
        if name in self.functions["global"]["vars"]:
            raise SemanticError(f"Nombre de función '{name}' ya usado como variable global")

        ret_addr = None
        if ret_type != "void":
            # Variable global reservada para el valor de retorno
            ret_addr = self.memory.alloc_var("glob", ret_type)
            self.functions["global"]["vars"][name] = VarInfo(name, ret_type, ret_addr)

        self.current_function = name
        self.functions[name] = {
            "ret": ret_type,
            "vars": {},
            "params": [],
            "start": None,
            "return_addr": ret_addr,
            "has_return": False,
        }

    def set_global(self):
        self.current_function = "global"

    def set_start(self, name, start):
        # Marca el índice de cuadruplo donde inicia la función
        self.functions[name]["start"] = start

    def mark_return(self, name):
        self.functions[name]["has_return"] = True

    def lookup_function(self, name):
        if name not in self.functions:
            raise SemanticError(f"Función '{name}' no declarada")
        return self.functions[name]

    def add_variable(self, name, var_type, address):
        # Agrega variable al ámbito actual con dirección ya reservada
        if name in self.functions[self.current_function]["vars"]:
            raise SemanticError(f"Variable '{name}' redeclarada en '{self.current_function}'")
        self.functions[self.current_function]["vars"][name] = VarInfo(
            name, var_type, address
        )

    def add_param(self, name, var_type):
        addr = self.memory.alloc_var("loc", var_type)
        self.functions[self.current_function]["params"].append(
            {"name": name, "type": var_type, "address": addr}
        )
        self.add_variable(name, var_type, addr)

    def lookup_variable(self, name):
        # Busca primero en el scope actual y luego en globales
        if name in self.functions[self.current_function]["vars"]:
            return self.functions[self.current_function]["vars"][name]
        if name in self.functions["global"]["vars"]:
            return self.functions["global"]["vars"][name]
        raise SemanticError(f"Variable '{name}' no declarada")
