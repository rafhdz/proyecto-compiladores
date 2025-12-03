from PatitoListener import PatitoListener
from PatitoParser import PatitoParser
from FuncDir import FuncDir
from VarTableHelper import VarTableHelper
from semantics import SemanticCube, SemanticError
from virtual_memory import VirtualMemory
from TempManager import TempManager
from quads import Quadruple
from opcodes import OPCODES

class PatitoSemanticListener(PatitoListener):

    def __init__(self):
        # === ESTRUCTURAS SEMÁNTICAS ===
        self.funcdir = FuncDir()
        self.vartab = VarTableHelper(self.funcdir)
        self.cube = SemanticCube()

        # === MEMORIA VIRTUAL ===
        self.memory = VirtualMemory()
        self.funcdir.memory = self.memory

        # Constantes: addr -> valor y lookup para evitar colisiones bool/int
        self.constants = {}
        self.constant_lookup = {}

        # === PILAS ===
        self.operand_stack = []
        self.type_stack = []
        self.operator_stack = []
        self.jump_stack = []

        # === CONTROL ===
        self.in_if_condition = False
        self.in_while_condition = False
        self.while_start_stack = []

        # === CUADRUPLOS ===
        self.quadruples = []
        self.temp_manager = TempManager(self.memory)
        self.goto_main_index = None
        # Rastrea el valor (addr, tipo) asociado a cada ExprContext
        self.expr_value = {}

    # ============================================================
    # DEBUG / SIMBOLOGÍA
    # ============================================================
    def build_symbol_table(self):
        """
        Crea un mapa direccion -> nombre amigable para imprimir cuádruplos
        con variables/constantes/temporales.
        """
        addr_to_name = {}

        # Variables globales
        for name, vinfo in self.funcdir.functions["global"]["vars"].items():
            addr_to_name[vinfo.address] = f"global.{name}"

        # Variables locales de cada función
        for fname, finfo in self.funcdir.functions.items():
            if fname == "global":
                continue
            for name, vinfo in finfo["vars"].items():
                addr_to_name[vinfo.address] = f"{fname}.{name}"

        # Constantes (valor -> addr está en self.constants)
        for addr, value in self.constants.items():
            addr_to_name[addr] = repr(value)

        # Temporales (guardados por TempManager)
        addr_to_name.update(self.temp_manager.addr_to_name)

        return addr_to_name

    # ============================================================
    # CONSTANTES
    # ============================================================
    def get_or_add_constant(self, value, vtype):
        # Evita duplicar direcciones para la misma constante/tipo
        key = (value, vtype)
        if key in self.constant_lookup:
            return self.constant_lookup[key]

        addr = self.memory.alloc_const(vtype)
        self.constant_lookup[key] = addr
        self.constants[addr] = value
        return addr

    # ============================================================
    # PROGRAMA Y BLOQUES
    # ============================================================
    def enterProgram(self, ctx):
        # Salto al inicio de main para omitir el código de funciones
        self.quadruples.append(Quadruple(OPCODES["GOTO"], None, None, None))
        self.goto_main_index = len(self.quadruples) - 1

    def enterBlock(self, ctx):
        parent = ctx.parentCtx

        # Inicio del bloque main
        if isinstance(parent, PatitoParser.ProgramContext):
            if self.goto_main_index is not None:
                self.quadruples[self.goto_main_index].res = len(self.quadruples)

        # Inicio de un bloque de función
        elif isinstance(parent, PatitoParser.FuncDeclContext):
            fname = parent.ID().getText()
            self.funcdir.set_start(fname, len(self.quadruples))
            # reiniciamos el contador de temporales para claridad
            self.temp_manager.counter = 0

    # ============================================================
    # DECLARACIONES
    # ============================================================
    def enterVarDecl(self, ctx):
        vtype = ctx.type_().getText()
        ids = [x.getText() for x in ctx.idList().ID()]
        for name in ids:
            self.vartab.add_var(name, vtype)

    def enterFuncDecl(self, ctx):
        ret_type = ctx.type_().getText()
        fname = ctx.ID().getText()
        self.funcdir.add_function(fname, ret_type)

        # Manejo de parámetros (esto sí se queda aquí)
        if ctx.paramList():
            for p in ctx.paramList().param():
                self.funcdir.add_param(
                    p.ID().getText(),
                    p.type_().getText()
                )

    def exitFuncDecl(self, ctx):
        fname = ctx.ID().getText()
        finfo = self.funcdir.lookup_function(fname)
        if finfo["start"] is None:
            self.funcdir.set_start(fname, len(self.quadruples))

        if finfo["ret"] != "void" and not finfo["has_return"]:
            raise SemanticError(f"La función '{fname}' debe retornar un valor")

        self.quadruples.append(Quadruple(OPCODES["ENDFUNC"], None, None, None))
        self.funcdir.set_global()

    # ============================================================
    # ÁTOMOS
    # ============================================================
    def exitAtom(self, ctx):
        # Cada átomo empuja su dirección y tipo a las pilas
        if ctx.ID():
            vinfo = self.vartab.lookup(ctx.ID().getText())
            self.operand_stack.append(vinfo.address)
            self.type_stack.append(vinfo.var_type)
            return

        if ctx.CTE_INT():
            value = int(ctx.CTE_INT().getText())
            addr = self.get_or_add_constant(value, "int")
            self.operand_stack.append(addr)
            self.type_stack.append("int")
            return

        if ctx.CTE_FLOAT():
            value = float(ctx.CTE_FLOAT().getText())
            addr = self.get_or_add_constant(value, "float")
            self.operand_stack.append(addr)
            self.type_stack.append("float")
            return

        if ctx.TRUE() or ctx.FALSE():
            value = True if ctx.TRUE() else False
            addr = self.get_or_add_constant(value, "bool")
            self.operand_stack.append(addr)
            self.type_stack.append("bool")
            return

        if ctx.STRING():
            txt = ctx.STRING().getText()
            addr = self.get_or_add_constant(txt, "string")
            self.operand_stack.append(addr)
            self.type_stack.append("string")
            return

    # ============================================================
    # OPERADORES BINARIOS: *, / 
    # ============================================================
    def exitMultOp(self, ctx):
        r_op = self.operand_stack.pop()
        r_ty = self.type_stack.pop()
        l_op = self.operand_stack.pop()
        l_ty = self.type_stack.pop()

        op = ctx.getChild(1).getText()
        res_ty = self.cube.check_op(op, l_ty, r_ty)

        _, addr = self.temp_manager.new_temp(res_ty)

        opcode = OPCODES[op]
        self.quadruples.append(Quadruple(opcode, l_op, r_op, addr))

        self.operand_stack.append(addr)
        self.type_stack.append(res_ty)

    # ============================================================
    # OPERADORES BINARIOS: +, -
    # ============================================================
    def exitAddOp(self, ctx):
        r_op = self.operand_stack.pop()
        r_ty = self.type_stack.pop()
        l_op = self.operand_stack.pop()
        l_ty = self.type_stack.pop()

        op = ctx.getChild(1).getText()
        res_ty = self.cube.check_op(op, l_ty, r_ty)

        _, addr = self.temp_manager.new_temp(res_ty)

        opcode = OPCODES[op]
        self.quadruples.append(Quadruple(opcode, l_op, r_op, addr))

        self.operand_stack.append(addr)
        self.type_stack.append(res_ty)

    # ============================================================
    # RELACIONALES
    # ============================================================
    def exitRelExpr(self, ctx):
        left_ctx = ctx.expr(0)
        right_ctx = ctx.expr(1)

        l_val = self.expr_value.get(left_ctx)
        r_val = self.expr_value.get(right_ctx)

        def pop_stack(side):
            if not self.operand_stack:
                return None
            return self.operand_stack.pop(), self.type_stack.pop()

        r_pair = r_val or pop_stack("right")
        l_pair = l_val or pop_stack("left")

        if not r_pair or not l_pair:
            stack_snapshot = list(self.operand_stack)
            raise SemanticError(
                f"Expresión relacional incompleta: '{ctx.getText()}', "
                f"stack={stack_snapshot}, in_if={self.in_if_condition}, in_while={self.in_while_condition}"
            )

        r_op, r_ty = r_pair
        l_op, l_ty = l_pair

        # Limpia de la pila si aún están presentes (sin afectar otros valores previos)
        if self.operand_stack and self.operand_stack[-1] == r_op:
            self.operand_stack.pop()
            self.type_stack.pop()
        if self.operand_stack and self.operand_stack[-1] == l_op:
            self.operand_stack.pop()
            self.type_stack.pop()

        op = ctx.relop().getText()
        res_ty = self.cube.check_op(op, l_ty, r_ty)

        _, addr = self.temp_manager.new_temp(res_ty)
        opcode = OPCODES[op]

        self.quadruples.append(Quadruple(opcode, l_op, r_op, addr))

        self.operand_stack.append(addr)
        self.type_stack.append(res_ty)
        self.expr_value[ctx] = (addr, res_ty)

        # IF -----------------------------------------------------
        if self.in_if_condition:
            cond = self.operand_stack.pop()
            self.type_stack.pop()
            self.quadruples.append(
                Quadruple(OPCODES["GOTOF"], cond, None, None)
            )
            self.jump_stack.append(len(self.quadruples) - 1)
            self.in_if_condition = False

        # WHILE --------------------------------------------------
        elif self.in_while_condition:
            cond = self.operand_stack.pop()
            self.type_stack.pop()
            self.quadruples.append(
                Quadruple(OPCODES["GOTOF"], cond, None, None)
            )
            self.jump_stack.append(len(self.quadruples) - 1)
            self.in_while_condition = False

    # ============================================================
    # ASIGNACIÓN
    # ============================================================
    def exitAssignStmt(self, ctx):
        name = ctx.ID().getText()
        vinfo = self.vartab.lookup(name)

        expr_addr = self.operand_stack.pop()
        expr_type = self.type_stack.pop()

        self.cube.check_assign(vinfo.var_type, expr_type)

        self.quadruples.append(
            Quadruple(OPCODES["="], expr_addr, None, vinfo.address)
        )

        # Si asignamos al nombre de la función actual, lo tratamos como retorno
        if (
            self.funcdir.current_function != "global"
            and name == self.funcdir.current_function
        ):
            finfo = self.funcdir.lookup_function(name)
            if finfo["ret"] == "void":
                raise SemanticError("Una función void no puede retornar un valor")
            self.quadruples.append(Quadruple(OPCODES["RET"], expr_addr, None, None))
            self.funcdir.mark_return(name)

    # ============================================================
    # PRINT
    # ============================================================
    def exitPrintStmt(self, ctx):
        if ctx.printArgList():
            count = len(ctx.printArgList().expr())
            if len(self.operand_stack) < count:
                raise SemanticError("Argumentos de print no evaluados correctamente")

            addrs = []
            for _ in range(count):
                addrs.append(self.operand_stack.pop())
                self.type_stack.pop()
            # Se agregan en orden de aparición (la pila invierte el orden)
            for addr in reversed(addrs):
                self.quadruples.append(
                    Quadruple(OPCODES["PRINT"], addr, None, None)
                )
        else:
            self.quadruples.append(
                Quadruple(OPCODES["PRINT"], None, None, None)
            )

    # ============================================================
    # LLAMADAS A FUNCIÓN
    # ============================================================
    def exitFuncCall(self, ctx):
        fname = ctx.ID().getText()
        finfo = self.funcdir.lookup_function(fname)

        # ERA
        self.quadruples.append(Quadruple(OPCODES["ERA"], None, None, fname))

        # Parámetros
        arg_exprs = ctx.argList().expr() if ctx.argList() else []
        arg_count = len(arg_exprs)
        expected_count = len(finfo["params"])

        if arg_count != expected_count:
            raise SemanticError(
                f"Número de argumentos inválido para '{fname}': "
                f"se esperaban {expected_count}, se recibieron {arg_count}"
            )

        if arg_count:
            arg_addrs = self.operand_stack[-arg_count:]
            arg_types = self.type_stack[-arg_count:]
        else:
            arg_addrs, arg_types = [], []

        for idx, (addr, ty) in enumerate(zip(arg_addrs, arg_types)):
            expected = finfo["params"][idx]["type"]
            self.cube.check_assign(expected, ty)
            target_addr = finfo["params"][idx]["address"]
            self.quadruples.append(
                Quadruple(OPCODES["PARAM"], addr, None, target_addr)
            )

        # limpiar de las pilas los argumentos
        for _ in range(arg_count):
            self.operand_stack.pop()
            self.type_stack.pop()

        # GOSUB
        if finfo["start"] is None:
            raise SemanticError(f"Función '{fname}' sin cuerpo definido")

        self.quadruples.append(
            Quadruple(OPCODES["GOSUB"], fname, None, finfo["start"])
        )

        # Valor de retorno
        parent = ctx.parentCtx
        is_stmt_call = isinstance(parent, PatitoParser.FuncCallStmtContext)

        if finfo["ret"] != "void":
            _, temp_addr = self.temp_manager.new_temp(finfo["ret"])
            ret_addr = finfo["return_addr"]
            self.quadruples.append(
                Quadruple(OPCODES["="], ret_addr, None, temp_addr)
            )
            if not is_stmt_call:
                self.operand_stack.append(temp_addr)
                self.type_stack.append(finfo["ret"])
        else:
            if not is_stmt_call:
                raise SemanticError(
                    f"La función '{fname}' es void y no puede usarse en expresiones"
                )

    # ============================================================
    # IF / ELSE
    # ============================================================
    def enterIfStmt(self, ctx):
        self.in_if_condition = True

    def exitIfStmt(self, ctx):
        # La lógica principal se maneja en exitRelExpr/exitToAdd + exitBlock
        return

    def exitBlock(self, ctx):
        parent = ctx.parentCtx

        if isinstance(parent, PatitoParser.IfStmtContext):
            blocks = parent.block()

            # THEN
            if ctx == blocks[0]:
                if parent.ELSE():
                    false_jump = self.jump_stack.pop()

                    self.quadruples.append(
                        Quadruple(OPCODES["GOTO"], None, None, None)
                    )
                    end_jump = len(self.quadruples) - 1
                    self.jump_stack.append(end_jump)

                    self.quadruples[false_jump].res = len(self.quadruples)

                else:
                    if self.jump_stack:
                        false_jump = self.jump_stack.pop()
                        self.quadruples[false_jump].res = len(self.quadruples)

            # ELSE
            elif len(blocks) > 1 and ctx == blocks[1]:
                if self.jump_stack:
                    end_jump = self.jump_stack.pop()
                    self.quadruples[end_jump].res = len(self.quadruples)

    # ============================================================
    # WHILE
    # ============================================================
    def enterWhileStmt(self, ctx):
        self.while_start_stack.append(len(self.quadruples))
        self.in_while_condition = True

    def exitWhileStmt(self, ctx):
        start = self.while_start_stack.pop()

        false_jump = self.jump_stack.pop()

        self.quadruples.append(
            Quadruple(OPCODES["GOTO"], None, None, start)
        )

        end = len(self.quadruples)
        self.quadruples[false_jump].res = end

    # ============================================================
    # UNARIO (+, -)
    # ============================================================
    def exitUnarySign(self, ctx):
        sign = ctx.getChild(0).getText()
        operand_addr = self.operand_stack.pop()
        operand_type = self.type_stack.pop()

        if sign == '+':
            # No-op, se vuelve a poner el operando
            self.operand_stack.append(operand_addr)
            self.type_stack.append(operand_type)
            return

        # signo negativo: 0 - op
        if operand_type not in ("int", "float"):
            raise SemanticError(f"No se puede aplicar signo a tipo {operand_type}")

        zero_val = 0.0 if operand_type == "float" else 0
        zero_addr = self.get_or_add_constant(zero_val, operand_type)

        _, temp_addr = self.temp_manager.new_temp(operand_type)
        self.quadruples.append(
            Quadruple(OPCODES["-"], zero_addr, operand_addr, temp_addr)
        )

        self.operand_stack.append(temp_addr)
        self.type_stack.append(operand_type)

    # ============================================================
    # CONDICIONES SIN OPERADOR RELACIONAL (usa expr -> addExpr)
    # ============================================================
    def exitToAdd(self, ctx):
        # Solo aplica cuando la expresión de condición no tuvo relop
        # y estamos evaluando directamente el expr del if/while.
        if not (self.in_if_condition or self.in_while_condition):
            # Registrar valor del expr si está en la pila
            if self.operand_stack:
                self.expr_value[ctx] = (self.operand_stack[-1], self.type_stack[-1])
            return

        # Detectar el statement al que pertenece esta expr, aunque no haya nodo Expr padre.
        stmt_ctx = None
        parent_expr = None
        if isinstance(ctx.parentCtx, (PatitoParser.IfStmtContext, PatitoParser.WhileStmtContext)):
            stmt_ctx = ctx.parentCtx
            parent_expr = ctx
        elif isinstance(ctx.parentCtx, PatitoParser.ExprContext):
            parent_expr = ctx.parentCtx
            if isinstance(parent_expr.parentCtx, (PatitoParser.IfStmtContext, PatitoParser.WhileStmtContext)):
                stmt_ctx = parent_expr.parentCtx

            # Si este addExpr es parte de una expr con operador relacional,
            # no generamos salto aquí; la lógica se maneja en exitRelExpr.
            if parent_expr.relop():
                if self.operand_stack:
                    self.expr_value[ctx] = (self.operand_stack[-1], self.type_stack[-1])
                return

        if stmt_ctx is None:
            if self.operand_stack:
                self.expr_value[ctx] = (self.operand_stack[-1], self.type_stack[-1])
            return

        # Validar que este expr sea el de la condición del if/while
        if isinstance(stmt_ctx, PatitoParser.IfStmtContext):
            if stmt_ctx.expr() != parent_expr:
                if self.operand_stack:
                    self.expr_value[ctx] = (self.operand_stack[-1], self.type_stack[-1])
                return
        else:  # WhileStmt
            if stmt_ctx.expr() != parent_expr:
                if self.operand_stack:
                    self.expr_value[ctx] = (self.operand_stack[-1], self.type_stack[-1])
                return

        cond_addr = self.operand_stack.pop()
        self.type_stack.pop()

        self.quadruples.append(Quadruple(OPCODES["GOTOF"], cond_addr, None, None))
        self.jump_stack.append(len(self.quadruples) - 1)

        if isinstance(stmt_ctx, PatitoParser.IfStmtContext):
            self.in_if_condition = False
        else:
            self.in_while_condition = False
        # Registrar el resultado booleano del expr
        self.expr_value[parent_expr] = (self.quadruples[-1].left, "int")

    # ============================================================
    # RETURN
    # ============================================================
    def exitReturnStmt(self, ctx):
        if self.funcdir.current_function == "global":
            raise SemanticError("Un return solo puede aparecer dentro de una función")

        finfo = self.funcdir.lookup_function(self.funcdir.current_function)
        if finfo["ret"] == "void":
            raise SemanticError("Una función void no puede retornar un valor")

        expr_addr = self.operand_stack.pop()
        expr_type = self.type_stack.pop()

        self.cube.check_assign(finfo["ret"], expr_type)

        # Guardar en la dirección reservada para el valor de retorno
        self.quadruples.append(
            Quadruple(OPCODES["="], expr_addr, None, finfo["return_addr"])
        )
        # Salida de la función
        self.quadruples.append(Quadruple(OPCODES["RET"], expr_addr, None, None))
        self.funcdir.mark_return(self.funcdir.current_function)
