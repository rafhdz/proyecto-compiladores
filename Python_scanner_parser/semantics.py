class SemanticError(Exception):
    # Errores semánticos detectados durante el análisis
    pass


class VarInfo:
    def __init__(self, var_type):
        self.var_type = var_type
        self.addr = None


class FuncInfo:
    def __init__(self, return_type):
        self.return_type = return_type
        self.params = []
        self.var_table = {}


class FuncDir:
    def __init__(self):
        self.funcs = {"global": FuncInfo("void")}
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
        if name in func.var_table:
            raise SemanticError(f"Parámetro '{name}' duplicado en '{self.current}'")
        func.params.append((name, param_type))
        func.var_table[name] = VarInfo(param_type)

    def lookup_function(self, name):
        if name not in self.funcs:
            raise SemanticError(f"Función '{name}' no declarada")
        return self.funcs[name]


class VarTableHelper:
    def __init__(self, funcdir: FuncDir):
        self.funcdir = funcdir

    def add_var(self, name, var_type):
        func = self.funcdir.get_current_funcinfo()
        if name in func.var_table:
            raise SemanticError(f"Variable '{name}' ya declarada en '{self.funcdir.current}'")
        func.var_table[name] = VarInfo(var_type)

    def lookup(self, name):
        # Resuelve primero en el alcance actual y luego en global
        f = self.funcdir.get_current_funcinfo()
        if name in f.var_table:
            return f.var_table[name]
        g = self.funcdir.funcs["global"]
        if name in g.var_table:
            return g.var_table[name]
        print(f"[Error semántico] Variable '{name}' no declarada.")
        return VarInfo("ERROR")

# Se asignan los tipos de datos, en base a la combinación 
class SemanticCube:
    def __init__(self):
        int_ops = {'int': 'int', 'float': 'float'}
        float_ops = {'int': 'float', 'float': 'float'}
        self.cube = {
            '+': {'int': int_ops, 'float': float_ops},
            '-': {'int': int_ops, 'float': float_ops},
            '*': {'int': int_ops, 'float': float_ops},
            '/': {'int': float_ops, 'float': float_ops},
            '%': {'int': {'int': 'int'}},
            '>': {'int': {'int': 'bool', 'float': 'bool'}, 'float': {'int': 'bool', 'float': 'bool'}},
            '<': {'int': {'int': 'bool', 'float': 'bool'}, 'float': {'int': 'bool', 'float': 'bool'}},
            '!=': {
                'int': {'int': 'bool', 'float': 'bool'},
                'float': {'int': 'bool', 'float': 'bool'},
                'bool': {'bool': 'bool'},
            },
            '==': {
                'int': {'int': 'bool', 'float': 'bool'},
                'float': {'int': 'bool', 'float': 'bool'},
                'bool': {'bool': 'bool'},
            },
        }

    def check_op(self, op, t1, t2):
        # Determina el tipo resultante de una operación binaria
        if t1 == 'ERROR' or t2 == 'ERROR':
            return 'ERROR'
        try:
            return self.cube[op][t1][t2]
        except KeyError:
            print(f"[Error semántico] Tipos incompatibles: {t1} {op} {t2}")
            return 'ERROR'

    def check_assign(self, target_type, expr_type):
        # Valida compatibilidad de tipos en asignaciones
        if target_type == 'float' and expr_type == 'int':
            return
        if target_type == 'bool' and expr_type == 'bool':
            return
        if target_type != expr_type:
            raise SemanticError(f"Asignación incompatible: {target_type} = {expr_type}")
