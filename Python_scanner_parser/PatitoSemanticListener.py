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
        right_op = self.operand_stack.pop()
        right_type = self.type_stack.pop()
        left_op = self.operand_stack.pop()
        left_type = self.type_stack.pop()

        op = ctx.relop().getText()
        res_type = self.cube.check_op(op, left_type, right_type)
        temp = self.temp_manager.new_temp()
        self.quadruples.append(Quadruple(op, left_op, right_op, temp))

        self.operand_stack.append(temp)
        self.type_stack.append(res_type)

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
            for _ in range(n):
                val = self.operand_stack.pop()
                self.type_stack.pop()
                self.quadruples.append(Quadruple('PRINT', val, None, None))
        else:
            self.quadruples.append(Quadruple('PRINT', None, None, None))

    # =============== CONDICIÓN (if / else) ===============
    def exitIfStmt(self, ctx: PatitoParser.IfStmtContext):
        hijos = [h.getText() for h in ctx.children]

        if len(self.operand_stack) > 0:
            cond_result = self.operand_stack.pop()
            cond_type = self.type_stack.pop() if len(self.type_stack) > 0 else 'ERROR'

            if cond_type != 'int':
                print("[Advertencia] Condición del 'if' no booleana, tipo:", cond_type)

            self.quadruples.append(Quadruple('GOTOF', cond_result, None, None))
            self.jump_stack.append(len(self.quadruples) - 1)
        else:
            print("[Aviso] No se encontró resultado de condición antes del 'if'.")

        if 'else' in hijos:
            self.quadruples.append(Quadruple('GOTO', None, None, None))
            false_jump = self.jump_stack.pop()
            self.quadruples[false_jump].res = len(self.quadruples)
            self.jump_stack.append(len(self.quadruples) - 1)
        else:
            if len(self.jump_stack) > 0:
                false_jump = self.jump_stack.pop()
                self.quadruples[false_jump].res = len(self.quadruples)
            else:
                print("[Aviso] No había GOTOF pendiente en if.")

    def exitBlock(self, ctx: PatitoParser.BlockContext):
        if len(self.jump_stack) > 0:
            top_index = self.jump_stack[-1]
            q = self.quadruples[top_index]
            if q.op == 'GOTO' and getattr(q, 'res', None) is None:
                q.res = len(self.quadruples)
                self.jump_stack.pop()

    # =============== CICLO (while / do) ===============
    def enterWhileStmt(self, ctx: PatitoParser.WhileStmtContext):
        self.jump_stack.append(len(self.quadruples))

    def exitWhileStmt(self, ctx: PatitoParser.WhileStmtContext):
        loop_start = self.jump_stack.pop()

        if len(self.operand_stack) > 0:
            cond_result = self.operand_stack.pop()
            cond_type = self.type_stack.pop() if len(self.type_stack) > 0 else 'ERROR'
            if cond_type != 'int':
                print("[Advertencia] Condición del while no booleana:", cond_type)
        else:
            print("[Aviso] No se encontró condición para while.")
            return

        self.quadruples.append(Quadruple('GOTOF', cond_result, None, None))
        false_jump = len(self.quadruples) - 1
        self.quadruples.append(Quadruple('GOTO', None, None, loop_start))

        end = len(self.quadruples)
        self.quadruples[false_jump].res = end