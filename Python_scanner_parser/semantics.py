# semantics.py

class SemanticError(Exception):
    pass


class VarInfo:
    def __init__(self, var_type):
        self.var_type = var_type
        self.addr = None  # placeholder para memoria virtual futura


class FuncInfo:
    def __init__(self, return_type):
        self.return_type = return_type
        self.params = []          # lista de (name, type)
        self.var_table = {}       # name -> VarInfo


class FuncDir:
    def __init__(self):
        # scope global como función virtual
        self.funcs = {
            "global": FuncInfo("void")
        }
        self.current = "global"

    def add_function(self, name, return_type):
        if name in self.funcs:
            raise SemanticError(f"Función '{name}' ya declarada")
        self.funcs[name] = FuncInfo(return_type)
        self.current = name

    def set_global(self):
        self.current = "global"

    def get_current_funcinfo(self):
        return self.funcs[self.current]

    def add_param(self, name, param_type):
        func = self.funcs[self.current]
        # también lo registramos como variable local
        if name in func.var_table:
            raise SemanticError(f"Parámetro '{name}' duplicado en función '{self.current}'")
        func.params.append((name, param_type))
        func.var_table[name] = VarInfo(param_type)

    def lookup_function(self, name):
        if name not in self.funcs:
            raise SemanticError(f"Función '{name}' no declarada")
        return self.funcs[name]


class VarTableHelper:
    """Ayuda a declarar/buscar variables respetando scope actual y global."""
    def __init__(self, funcdir: FuncDir):
        self.funcdir = funcdir

    def add_var(self, name, var_type):
        func = self.funcdir.get_current_funcinfo()
        if name in func.var_table:
            raise SemanticError(f"Variable '{name}' ya declarada en '{self.funcdir.current}'")
        func.var_table[name] = VarInfo(var_type)

    def lookup(self, name):
        # busca en current
        func = self.funcdir.get_current_funcinfo()
        if name in func.var_table:
            return func.var_table[name]
        # busca en global
        glob = self.funcdir.funcs["global"]
        if name in glob.var_table:
            return glob.var_table[name]
        raise SemanticError(f"Variable '{name}' no declarada")


class SemanticCube:
    def __init__(self):
        # operador -> izq -> der -> result
        int_ops = {
            'int': 'int',
            'float': 'float'
        }
        float_ops = {
            'int': 'float',
            'float': 'float'
        }
        # base
        self.cube = {
            '+': {
                'int': int_ops,
                'float': float_ops,
            },
            '-': {
                'int': int_ops,
                'float': float_ops,
            },
            '*': {
                'int': int_ops,
                'float': float_ops,
            },
            '/': {
                'int': float_ops,   # división regresa float
                'float': float_ops,
            },
            '>': {
                'int': {'int': 'int', 'float': 'int'},
                'float': {'int': 'int', 'float': 'int'},
            },
            '<': {
                'int': {'int': 'int', 'float': 'int'},
                'float': {'int': 'int', 'float': 'int'},
            },
            '!=': {
                'int': {'int': 'int', 'float': 'int'},
                'float': {'int': 'int', 'float': 'int'},
            },
        }

    def check_op(self, op, t1, t2):
        try:
            return self.cube[op][t1][t2]
        except KeyError:
            raise SemanticError(f"Tipos incompatibles: {t1} {op} {t2}")

    def check_assign(self, target_type, expr_type):
        # float = int permitido
        if target_type == 'float' and expr_type == 'int':
            return
        if target_type != expr_type:
            raise SemanticError(f"Asignación incompatible: {target_type} = {expr_type}")