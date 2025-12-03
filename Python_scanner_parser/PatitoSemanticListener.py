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
    """
    Listener semántico del lenguaje Patito.

    ANTLR recorre el Parse Tree en preorden e invoca:
        enterX(context) -> al llegar a un nodo
        exitX(context)  -> al terminar el nodo

    Aquí hacemos:
        - Verificación semántica
        - Asignación de memoria virtual
        - Generación de cuádruplos

    Esto es fase FRONTEND del compilador:
        1. Scanner: convierte texto en tokens
        2. Parser: tokens → árbol sintáctico
        3. Listener: árbol sintáctico → semántica + código intermedio
    """

    def __init__(self):
        # ============================================================
        # TABLAS PRINCIPALES DE COMPILACIÓN
        # ============================================================

        # Directorio de funciones: cada función tiene:
        # params, tabla local, tipo retorno, dir retorno, dir inicio
        self.funcdir = FuncDir()

        # Variable table helper: decide si registrar/buscar en global o función actual
        self.vartab = VarTableHelper(self.funcdir)

        # Cubo semántico: define tipos + operadores válidos y resultado esperado
        self.cube = SemanticCube()

        # ============================================================
        # MEMORIA VIRTUAL
        # ============================================================

        # Maneja direcciones reales:
        #    Global, Local, Temporal, Constantes
        self.memory = VirtualMemory()
        # FuncDir debe poder pedir memoria (para vars, ret_addr, params)
        self.funcdir.memory = self.memory

        # Constantes únicas:
        #   constant_lookup → (valor,tipo) → addr
        #   constants → addr → valor
        self.constants = {}
        self.constant_lookup = {}

        # ============================================================
        # PILAS SEMÁNTICAS
        # ============================================================
        # Aquí se simula el STACK MACHINE del compilador

        # Direcciones de operandos (nunca valores reales)
        self.operand_stack = []
        # Tipos ("int","float","bool"...)
        self.type_stack = []
        # Operadores: en esta versión rara vez se usa
        self.operator_stack = []
        # Saltos pendientes de rellenar (backpatch)
        self.jump_stack = []

        # ============================================================
        # CONTROL DE CONTEXTO
        # ============================================================
        # Estas flags son necesarias porque la gramática permite:
        #   if(expr)
        #   if(expr relop expr)
        # Sin estas flags, el listener no sabe cuándo expr pertenece a un IF/WHILE
        self.in_if_condition = False
        self.in_while_condition = False

        # Guarda el índice del inicio del ciclo while
        # para generar el salto hacia atrás
        self.while_start_stack = []

        # ============================================================
        # CUADRUPLOS
        # ============================================================
        self.quadruples = []

        # Gestor de temporales: pide direcciones
        self.temp_manager = TempManager(self.memory)

        # Posición del GOTO que saltará al MAIN
        self.goto_main_index = None

        # Cache de expr → (addr,tipo)
        # Esto soluciona bugs de ANTLR donde exitRelExpr consumía pilas erróneamente
        self.expr_value = {}

    # ============================================================
    # UTILIDAD PARA DEBUG → mapping dirección → nombre humano
    # ============================================================
    def build_symbol_table(self):
        """
        Construye un mapa addr → string amigable.
        Solo para depuración/pretty print.
        No altera generación de código.
        """
        addr_to_name = {}

        # Variables globales
        for name, vinfo in self.funcdir.functions["global"]["vars"].items():
            addr_to_name[vinfo.address] = f"global.{name}"

        # Variables locales
        for fname, finfo in self.funcdir.functions.items():
            if fname == "global":
                continue
            for name, vinfo in finfo["vars"].items():
                addr_to_name[vinfo.address] = f"{fname}.{name}"

        # Constantes
        for addr, value in self.constants.items():
            addr_to_name[addr] = repr(value)

        # Temporales asignados por TempManager
        addr_to_name.update(self.temp_manager.addr_to_name)

        return addr_to_name

    # ============================================================
    # CONSTANTES
    # ============================================================
    def get_or_add_constant(self, value, vtype):
        """
        Garantiza una constante única.
        Sin duplicar direcciones
        """
        key = (value, vtype)

        # Ya existe → devuelve misma dirección
        if key in self.constant_lookup:
            return self.constant_lookup[key]

        # Reserva espacio en segmento CONST
        addr = self.memory.alloc_const(vtype)

        self.constant_lookup[key] = addr
        self.constants[addr] = value
        return addr

    # ============================================================
    # PROGRAM
    # ============================================================
    def enterProgram(self, ctx):
        """
        Estrategia compilador:
        - ANTES del main se generan funciones
        - PERO la ejecución real debe empezar en main
        Solución:
            GOTO ?
            cuando lleguemos al bloque de MAIN se rellena
        """
        self.quadruples.append(Quadruple(OPCODES["GOTO"], None, None, None))
        self.goto_main_index = len(self.quadruples) - 1

    # ============================================================
    # BLOQUES
    # ============================================================
    def enterBlock(self, ctx):
        parent = ctx.parentCtx

        # Bloque MAIN (padre es ProgramContext)
        if isinstance(parent, PatitoParser.ProgramContext):
            # backpatch GOTO al inicio del main
            if self.goto_main_index is not None:
                self.quadruples[self.goto_main_index].res = len(self.quadruples)

        # Bloque de función
        elif isinstance(parent, PatitoParser.FuncDeclContext):
            fname = parent.ID().getText()
            # Cuádruplo donde inicia el código ejecutable
            self.funcdir.set_start(fname, len(self.quadruples))
            # reset temporales → buena práctica / debug
            self.temp_manager.counter = 0

    # ============================================================
    # DECLARACIONES
    # ============================================================
    def enterVarDecl(self, ctx):
        """
        varDecl: idList : type;
        Cada ID genera una dirección nueva en el segmento:
        - Global si estamos en global
        - Local si estamos dentro de función
        """
        vtype = ctx.type_().getText()
        ids = [x.getText() for x in ctx.idList().ID()]
        for name in ids:
            self.vartab.add_var(name, vtype)

    def enterFuncDecl(self, ctx):
        """
        type ID(params)
        Registrar función en directorio:
        - tipo retorno
        - parámetros (pero aún no set_start)
        """
        ret_type = ctx.type_().getText()
        fname = ctx.ID().getText()
        self.funcdir.add_function(fname, ret_type)

        # Agregar parámetros a tabla local
        if ctx.paramList():
            for p in ctx.paramList().param():
                self.funcdir.add_param(
                    p.ID().getText(),
                    p.type_().getText()
                )

    def exitFuncDecl(self, ctx):
        """
        Al salir:
            - Verificar RETURN obligatorio
            - INYECTAR ENDFUNC
            - Regresar a contexto global
        """
        fname = ctx.ID().getText()
        finfo = self.funcdir.lookup_function(fname)

        # Si nunca se entró al block
        if finfo["start"] is None:
            self.funcdir.set_start(fname, len(self.quadruples))

        # Función no void → debe retornar
        if finfo["ret"] != "void" and not finfo["has_return"]:
            raise SemanticError(f"La función '{fname}' debe retornar un valor")

        self.quadruples.append(Quadruple(OPCODES["ENDFUNC"], None, None, None))
        self.funcdir.set_global()

    # ============================================================
    # ATOMS (hojas de expresiones)
    # ============================================================
    def exitAtom(self, ctx):
        """
        ID → dirección de var
        CTE → dirección const
        STRING → dirección const
        TRUE/FALSE → dirección const
        """
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
    # OPERADORES BINARIOS * /
    # ============================================================
    def exitMultOp(self, ctx):
        """
        multExpr (*) unaryExpr
        ANTLR ya dejó ambos operandos evaluados en la pila
        """
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
    # OPERADORES BINARIOS + -
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
    # EXPRESIONES RELACIONALES
    # ============================================================
    def exitRelExpr(self, ctx):
        """
        expr relop expr
        Produce temporal booleano y si estamos en IF/WHILE → GOTOF
        """
        left_ctx = ctx.expr(0)
        right_ctx = ctx.expr(1)

        # expr_value almacena pares cuando exitToAdd los guarda
        l_val = self.expr_value.get(left_ctx)
        r_val = self.expr_value.get(right_ctx)

        # fallback: use pop del stack
        def pop_stack(side):
            if not self.operand_stack:
                return None
            return self.operand_stack.pop(), self.type_stack.pop()

        r_pair = r_val or pop_stack("right")
        l_pair = l_val or pop_stack("left")

        if not r_pair or not l_pair:
            raise SemanticError(
                f"Expresión relacional incompleta: '{ctx.getText()}', "
            )

        r_op, r_ty = r_pair
        l_op, l_ty = l_pair

        # por si quedaron duplicados arriba en la pila
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

        # IF → GOTOF
        if self.in_if_condition:
            cond = self.operand_stack.pop()
            self.type_stack.pop()
            self.quadruples.append(
                Quadruple(OPCODES["GOTOF"], cond, None, None)
            )
            self.jump_stack.append(len(self.quadruples) - 1)
            self.in_if_condition = False

        # WHILE → GOTOF
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
        """
        ID = expr;
        expr dejó valor en operand_stack
        """
        name = ctx.ID().getText()
        vinfo = self.vartab.lookup(name)

        expr_addr = self.operand_stack.pop()
        expr_type = self.type_stack.pop()

        self.cube.check_assign(vinfo.var_type, expr_type)

        self.quadruples.append(
            Quadruple(OPCODES["="], expr_addr, None, vinfo.address)
        )

        # Trick: asignar al nombre de la función → return implícito
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
        """
        print(expr, expr,...)
        Se evalúan todas las expr antes, así que
        operand_stack ya contiene direcciones
        """
        if ctx.printArgList():
            count = len(ctx.printArgList().expr())
            if len(self.operand_stack) < count:
                raise SemanticError("Argumentos de print no evaluados correctamente")

            addrs = []
            for _ in range(count):
                addrs.append(self.operand_stack.pop())
                self.type_stack.pop()

            # pila invierte orden → revertir
            for addr in reversed(addrs):
                self.quadruples.append(
                    Quadruple(OPCODES["PRINT"], addr, None, None)
                )
        else:
            self.quadruples.append(
                Quadruple(OPCODES["PRINT"], None, None, None)
            )

    # ============================================================
    # LLAMADA A FUNCIÓN COMO EXPRESIÓN O STATEMENT
    # ============================================================
    def exitFuncCall(self, ctx):
        """
        Genera:
          ERA fname
          PARAM (...)
          GOSUB fname, start
          = return_addr, temp
        """
        fname = ctx.ID().getText()
        finfo = self.funcdir.lookup_function(fname)

        # Crear AR de llamada
        self.quadruples.append(Quadruple(OPCODES["ERA"], None, None, fname))

        # Extraer args
        arg_exprs = ctx.argList().expr() if ctx.argList() else []
        arg_count = len(arg_exprs)
        expected_count = len(finfo["params"])

        if arg_count != expected_count:
            raise SemanticError(
                f"Número de argumentos inválido para '{fname}': "
                f"esperado {expected_count}, recibido {arg_count}"
            )

        if arg_count:
            arg_addrs = self.operand_stack[-arg_count:]
            arg_types = self.type_stack[-arg_count:]
        else:
            arg_addrs, arg_types = [], []

        # PARAM
        for idx, (addr, ty) in enumerate(zip(arg_addrs, arg_types)):
            expected = finfo["params"][idx]["type"]
            self.cube.check_assign(expected, ty)
            target_addr = finfo["params"][idx]["address"]
            self.quadruples.append(
                Quadruple(OPCODES["PARAM"], addr, None, target_addr)
            )

        # limpiar args de pilas
        for _ in range(arg_count):
            self.operand_stack.pop()
            self.type_stack.pop()

        # Llamada efectiva
        if finfo["start"] is None:
            raise SemanticError(f"Función '{fname}' sin cuerpo definido")

        self.quadruples.append(
            Quadruple(OPCODES["GOSUB"], fname, None, finfo["start"])
        )

        # Manejo de return
        parent = ctx.parentCtx
        is_stmt_call = isinstance(parent, PatitoParser.FuncCallStmtContext)

        if finfo["ret"] != "void":
            _, temp_addr = self.temp_manager.new_temp(finfo["ret"])
            ret_addr = finfo["return_addr"]
            self.quadruples.append(
                Quadruple(OPCODES["="], ret_addr, None, temp_addr)
            )
            # si es parte de expresión
            if not is_stmt_call:
                self.operand_stack.append(temp_addr)
                self.type_stack.append(finfo["ret"])
        else:
            # función void NO puede estar en expr
            if not is_stmt_call:
                raise SemanticError(
                    f"La función '{fname}' es void y no puede usarse en expresiones"
                )

    # ============================================================
    # IF
    # ============================================================
    def enterIfStmt(self, ctx):
        """
        Siguiente expr será condición
        """
        self.in_if_condition = True

    def exitIfStmt(self, ctx):
        """
        Lógica principal en exitBlock
        """
        return

    def exitBlock(self, ctx):
        """
        Este método maneja backpatch de:
         - falso → inicio ELSE
         - GOTO → salida IF
         - salida ELSE
        """
        parent = ctx.parentCtx

        # Bloques del IF
        if isinstance(parent, PatitoParser.IfStmtContext):
            blocks = parent.block()

            # THEN
            if ctx == blocks[0]:
                if parent.ELSE():
                    false_jump = self.jump_stack.pop()
                    # Saltar ELSE
                    self.quadruples.append(
                        Quadruple(OPCODES["GOTO"], None, None, None)
                    )
                    end_jump = len(self.quadruples) - 1
                    self.jump_stack.append(end_jump)

                    # GOTOF → inicio ELSE
                    self.quadruples[false_jump].res = len(self.quadruples)
                else:
                    # IF sin else
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
        """
        Registrar índice del inicio de la condición
        """
        self.while_start_stack.append(len(self.quadruples))
        self.in_while_condition = True

    def exitWhileStmt(self, ctx):
        """
        1. GOTO → inicio condición
        2. Backpatch GOTOF → salida
        """
        start = self.while_start_stack.pop()
        false_jump = self.jump_stack.pop()

        self.quadruples.append(
            Quadruple(OPCODES["GOTO"], None, None, start)
        )

        end = len(self.quadruples)
        self.quadruples[false_jump].res = end

    # ============================================================
    # UNARIOS
    # ============================================================
    def exitUnarySign(self, ctx):
        """
        +x → sin efecto
        -x → generar 0 - x
        """
        sign = ctx.getChild(0).getText()
        operand_addr = self.operand_stack.pop()
        operand_type = self.type_stack.pop()

        if sign == '+':
            self.operand_stack.append(operand_addr)
            self.type_stack.append(operand_type)
            return

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
    # CONDICIÓN SIN OP RELACIONAL (expr simple)
    # ============================================================
    def exitToAdd(self, ctx):
        """
        expr sin relop
        Puede ser condición de IF/WHILE → GOTOF
        """
        if not (self.in_if_condition or self.in_while_condition):
            if self.operand_stack:
                self.expr_value[ctx] = (self.operand_stack[-1], self.type_stack[-1])
            return

        # Detección del contexto padre real
        stmt_ctx = None
        parent_expr = None
        if isinstance(ctx.parentCtx, (PatitoParser.IfStmtContext, PatitoParser.WhileStmtContext)):
            stmt_ctx = ctx.parentCtx
            parent_expr = ctx
        elif isinstance(ctx.parentCtx, PatitoParser.ExprContext):
            parent_expr = ctx.parentCtx
            if isinstance(parent_expr.parentCtx, (PatitoParser.IfStmtContext, PatitoParser.WhileStmtContext)):
                stmt_ctx = parent_expr.parentCtx

            if parent_expr.relop():
                if self.operand_stack:
                    self.expr_value[ctx] = (self.operand_stack[-1], self.type_stack[-1])
                return

        if stmt_ctx is None:
            if self.operand_stack:
                self.expr_value[ctx] = (self.operand_stack[-1], self.type_stack[-1])
            return

        # Validar que este expr es realmente el condicional
        if isinstance(stmt_ctx, PatitoParser.IfStmtContext):
            if stmt_ctx.expr() != parent_expr:
                return
        else:
            if stmt_ctx.expr() != parent_expr:
                return

        # Generar GOTOF directo
        cond_addr = self.operand_stack.pop()
        self.type_stack.pop()

        self.quadruples.append(Quadruple(OPCODES["GOTOF"], cond_addr, None, None))
        self.jump_stack.append(len(self.quadruples) - 1)

        # Reset banderas
        if isinstance(stmt_ctx, PatitoParser.IfStmtContext):
            self.in_if_condition = False
        else:
            self.in_while_condition = False

        self.expr_value[parent_expr] = (self.quadruples[-1].left, "int")

    # ============================================================
    # RETURN
    # ============================================================
    def exitReturnStmt(self, ctx):
        """
        return(expr)
        1. expr en pila
        2. mover a return_addr
        3. emitir RET
        """
        if self.funcdir.current_function == "global":
            raise SemanticError("Un return solo puede aparecer dentro de una función")

        finfo = self.funcdir.lookup_function(self.funcdir.current_function)
        if finfo["ret"] == "void":
            raise SemanticError("Una función void no puede retornar un valor")

        expr_addr = self.operand_stack.pop()
        expr_type = self.type_stack.pop()

        self.cube.check_assign(finfo["ret"], expr_type)

        self.quadruples.append(
            Quadruple(OPCODES["="], expr_addr, None, finfo["return_addr"])
        )
        self.quadruples.append(Quadruple(OPCODES["RET"], expr_addr, None, None))
        self.funcdir.mark_return(self.funcdir.current_function)
