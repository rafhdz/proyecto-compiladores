from PatitoListener import PatitoListener
from PatitoParser import PatitoParser
from semantics import FuncDir, VarTableHelper, SemanticCube
from quads import Quadruple, TempManager


class PatitoSemanticListener(PatitoListener):
    def __init__(self):
        # Estructuras semánticas
        self.funcdir = FuncDir()
        self.vartab = VarTableHelper(self.funcdir)
        self.cube = SemanticCube()

        # Pilas
        self.operand_stack = []
        self.type_stack = []
        self.operator_stack = []
        self.jump_stack = []  

        # Para controlar en qué parte estamos (condiciones)
        self.in_if_condition = False
        self.in_while_condition = False

        # Para while: dirección de inicio de cada ciclo
        self.while_start_stack = []

        # Cuádruplos
        self.quadruples = []
        self.temp_manager = TempManager()

    # =============== DECLARACIONES ===============
    def enterVarDecl(self, ctx: PatitoParser.VarDeclContext):
        var_type = ctx.type_().getText()
        ids = [x.getText() for x in ctx.idList().ID()]
        for name in ids:
            self.vartab.add_var(name, var_type)

    def enterFuncDecl(self, ctx: PatitoParser.FuncDeclContext):
        ret_type = ctx.type_().getText()
        func_name = ctx.ID().getText()
        self.funcdir.add_function(func_name, ret_type)

        # Parámetros
        if ctx.paramList():
            for p in ctx.paramList().param():
                pname = p.ID().getText()
                ptype = p.type_().getText()
                self.funcdir.add_param(pname, ptype)

        # Variables locales
        if ctx.funcVarSection():
            for v in ctx.funcVarSection().varDecl():
                vtype = v.type_().getText()
                ids = [x.getText() for x in v.idList().ID()]
                for name in ids:
                    self.vartab.add_var(name, vtype)

    def exitFuncDecl(self, ctx: PatitoParser.FuncDeclContext):
        self.funcdir.set_global()

    # =============== EXPRESIONES ===============
    def exitAtom(self, ctx: PatitoParser.AtomContext):
        if ctx.ID():
            name = ctx.ID().getText()
            vinfo = self.vartab.lookup(name)
            self.operand_stack.append(name)
            self.type_stack.append(vinfo.var_type)
        elif ctx.CTE_INT():
            val = int(ctx.CTE_INT().getText())
            self.operand_stack.append(val)
            self.type_stack.append('int')
        elif ctx.CTE_FLOAT():
            val = float(ctx.CTE_FLOAT().getText())
            self.operand_stack.append(val)
            self.type_stack.append('float')
        elif ctx.STRING():
            self.operand_stack.append(ctx.STRING().getText())
            self.type_stack.append('string')

    def exitMultOp(self, ctx: PatitoParser.MultOpContext):
        right_op = self.operand_stack.pop()
        right_type = self.type_stack.pop()
        left_op = self.operand_stack.pop()
        left_type = self.type_stack.pop()

        op = ctx.getChild(1).getText()
        res_type = self.cube.check_op(op, left_type, right_type)
        temp = self.temp_manager.new_temp()
        self.quadruples.append(Quadruple(op, left_op, right_op, temp))

        self.operand_stack.append(temp)
        self.type_stack.append(res_type)

    def exitAddOp(self, ctx: PatitoParser.AddOpContext):
        right_op = self.operand_stack.pop()
        right_type = self.type_stack.pop()
        left_op = self.operand_stack.pop()
        left_type = self.type_stack.pop()

        op = ctx.getChild(1).getText()
        res_type = self.cube.check_op(op, left_type, right_type)
        temp = self.temp_manager.new_temp()
        self.quadruples.append(Quadruple(op, left_op, right_op, temp))

        self.operand_stack.append(temp)
        self.type_stack.append(res_type)

    def exitRelExpr(self, ctx: PatitoParser.RelExprContext):
        # Primero generamos el cuadruplo relacional normal
        right_op = self.operand_stack.pop()
        right_type = self.type_stack.pop()
        left_op = self.operand_stack.pop()
        left_type = self.type_stack.pop()

        op = ctx.relop().getText()
        res_type = self.cube.check_op(op, left_type, right_type)
        temp = self.temp_manager.new_temp()
        self.quadruples.append(Quadruple(op, left_op, right_op, temp))

        # Resultado de la expresión relacional
        self.operand_stack.append(temp)
        self.type_stack.append(res_type)

        # ---- Condición de IF ----
        if self.in_if_condition:
            cond_result = self.operand_stack.pop()
            cond_type = self.type_stack.pop()
            if cond_type != 'int':
                print("[Advertencia] Condición del 'if' no booleana, tipo:", cond_type)

            # GOTOF cond, -, ?
            self.quadruples.append(Quadruple('GOTOF', cond_result, None, None))
            self.jump_stack.append(len(self.quadruples) - 1)
            self.in_if_condition = False

        # ---- Condición de WHILE ----
        elif self.in_while_condition:
            cond_result = self.operand_stack.pop()
            cond_type = self.type_stack.pop()
            if cond_type != 'int':
                print("[Advertencia] Condición del 'while' no booleana, tipo:", cond_type)

            # GOTOF cond, -, ?
            self.quadruples.append(Quadruple('GOTOF', cond_result, None, None))
            self.jump_stack.append(len(self.quadruples) - 1)
            self.in_while_condition = False

    # =============== ASIGNACIÓN ===============
    def exitAssignStmt(self, ctx: PatitoParser.AssignStmtContext):
        var_name = ctx.ID().getText()
        var_info = self.vartab.lookup(var_name)
        expr_res = self.operand_stack.pop()
        expr_type = self.type_stack.pop()
        self.cube.check_assign(var_info.var_type, expr_type)
        self.quadruples.append(Quadruple('=', expr_res, None, var_name))

    # =============== PRINT ===============
    def exitPrintStmt(self, ctx: PatitoParser.PrintStmtContext):
        if ctx.printArgList():
            n = len(ctx.printArgList().expr())
            values = []
            # Sacamos de la pila, pero se quedan en orden inverso
            for _ in range(n):
                val = self.operand_stack.pop()
                self.type_stack.pop()
                values.append(val)
            # Volvemos a imprimir en el orden original: izquierda -> derecha
            for val in reversed(values):
                self.quadruples.append(Quadruple('PRINT', val, None, None))
        else:
            self.quadruples.append(Quadruple('PRINT', None, None, None))

    # =============== CONDICIÓN (if / else) ===============

    def enterIfStmt(self, ctx: PatitoParser.IfStmtContext):
        """
        Cuando entramos al if, sabemos que viene una condición (expr).
        Marcamos que la siguiente expresión relacional que salga pertenece al if.
        """
        self.in_if_condition = True

    def exitIfStmt(self, ctx: PatitoParser.IfStmtContext):
        """
        Aquí ya se ejecutaron los bloques y exitBlock se encargó de hacer
        el backpatch de los saltos. No necesitamos hacer nada más.
        """
        pass

    # =============== BLOQUES (necesarios para el manejo if / else) ===============
    def exitBlock(self, ctx: PatitoParser.BlockContext):
        """
        Este método ahora solo maneja el cierre de bloques de IF.
        Se asume que el GOTOF de la condición ya se generó en exitRelExpr.
        """
        parent = ctx.parentCtx

        # Solo nos interesa si el padre es un if
        if isinstance(parent, PatitoParser.IfStmtContext):
            blocks = parent.block()

            # ¿Estamos saliendo del bloque THEN?
            if ctx == blocks[0]:
                if parent.ELSE() is not None:
                    # Hay ELSE:
                    # 1) Sacamos el GOTOF pendiente (brinco al else)
                    false_jump = self.jump_stack.pop()

                    # 2) Generamos un GOTO al final del if (lo parcheamos al final del else)
                    self.quadruples.append(Quadruple('GOTO', None, None, None))
                    end_jump = len(self.quadruples) - 1
                    self.jump_stack.append(end_jump)

                    # 3) El GOTOF ahora debe apuntar al inicio del else (siguiente cuadruplo)
                    self.quadruples[false_jump].res = len(self.quadruples)
                else:
                    # No hay ELSE: el GOTOF debe apuntar al siguiente cuadruplo
                    if self.jump_stack:
                        false_jump = self.jump_stack.pop()
                        self.quadruples[false_jump].res = len(self.quadruples)

            # ¿Estamos saliendo del bloque ELSE?
            elif len(blocks) > 1 and ctx == blocks[1]:
                # Parcheamos el GOTO del final del THEN para que salte al final del ELSE
                if self.jump_stack:
                    end_jump = self.jump_stack.pop()
                    self.quadruples[end_jump].res = len(self.quadruples)

    # =============== CICLO (while / do) ===============
    def enterWhileStmt(self, ctx: PatitoParser.WhileStmtContext):
        # Dirección de inicio del ciclo (donde empieza la evaluación de la condición)
        self.while_start_stack.append(len(self.quadruples))
        # La siguiente expresión relacional que salga será la condición del while
        self.in_while_condition = True

    def exitWhileStmt(self, ctx: PatitoParser.WhileStmtContext):
        # Recuperamos inicio del ciclo
        loop_start = self.while_start_stack.pop()

        # El GOTOF de la condición ya fue generado en exitRelExpr
        if not self.jump_stack:
            print("[Aviso] No se encontró GOTOF pendiente para while.")
            return

        false_jump = self.jump_stack.pop()

        # GOTO al inicio del ciclo
        self.quadruples.append(Quadruple('GOTO', None, None, loop_start))

        # El GOTOF salta al cuadruplo siguiente (fin del while)
        end = len(self.quadruples)
        self.quadruples[false_jump].res = end