# PatitoSemanticListener.py

from PatitoListener import PatitoListener
from PatitoParser import PatitoParser
from semantics import FuncDir, VarTableHelper, SemanticCube
from quads import Quadruple, TempManager

class PatitoSemanticListener(PatitoListener):
    def __init__(self):
        # estructuras semánticas
        self.funcdir = FuncDir()
        self.vartab = VarTableHelper(self.funcdir)
        self.cube = SemanticCube()

        # PILAS
        self.operand_stack = []   # valores/ids/temporales
        self.type_stack = []      # tipos de cada operando
        self.operator_stack = []  # por si quieres manejar operadores explícitos

        # CUADRUPLOS
        self.quadruples = []
        self.temp_manager = TempManager()

    # =============== DECLARACIONES ===============
    def enterVarDecl(self, ctx:PatitoParser.VarDeclContext):
        var_type = ctx.type_().getText()
        ids = [x.getText() for x in ctx.idList().ID()]
        for name in ids:
            self.vartab.add_var(name, var_type)

    def enterFuncDecl(self, ctx:PatitoParser.FuncDeclContext):
        ret_type = ctx.type_().getText()
        func_name = ctx.ID().getText()
        self.funcdir.add_function(func_name, ret_type)
        if ctx.paramList():
            for p in ctx.paramList().param():
                self.funcdir.add_param(p.ID().getText(), p.type_().getText())
        if ctx.funcVarSection():
            for v in ctx.funcVarSection().varDecl():
                vtype = v.type_().getText()
                ids = [x.getText() for x in v.idList().ID()]
                for name in ids:
                    self.vartab.add_var(name, vtype)

    def exitFuncDecl(self, ctx:PatitoParser.FuncDeclContext):
        self.funcdir.set_global()

    # =============== EXPRESIONES ===============
    # atom: ID | CTE_INT | CTE_FLOAT | STRING | (expr)
    def exitAtom(self, ctx:PatitoParser.AtomContext):
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
        # si es (expr) no hacemos nada: la expr ya dejó su resultado en la pila

    # multExpr: multExpr (*|/) unaryExpr
    def exitMultOp(self, ctx:PatitoParser.MultOpContext):
        right_op = self.operand_stack.pop()
        right_type = self.type_stack.pop()
        left_op = self.operand_stack.pop()
        left_type = self.type_stack.pop()

        op = ctx.getChild(1).getText()  # * o /
        res_type = self.cube.check_op(op, left_type, right_type)

        temp = self.temp_manager.new_temp()
        self.quadruples.append(Quadruple(op, left_op, right_op, temp))

        self.operand_stack.append(temp)
        self.type_stack.append(res_type)

    # addExpr: addExpr (+|-) multExpr
    def exitAddOp(self, ctx:PatitoParser.AddOpContext):
        right_op = self.operand_stack.pop()
        right_type = self.type_stack.pop()
        left_op = self.operand_stack.pop()
        left_type = self.type_stack.pop()

        op = ctx.getChild(1).getText()  # + o -
        res_type = self.cube.check_op(op, left_type, right_type)

        temp = self.temp_manager.new_temp()
        self.quadruples.append(Quadruple(op, left_op, right_op, temp))

        self.operand_stack.append(temp)
        self.type_stack.append(res_type)

    # expr: expr relop expr
    def exitRelExpr(self, ctx:PatitoParser.RelExprContext):
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
    # assignStmt : ID ASSIGN expr SEMI
    def exitAssignStmt(self, ctx:PatitoParser.AssignStmtContext):
        var_name = ctx.ID().getText()
        var_info = self.vartab.lookup(var_name)

        expr_res = self.operand_stack.pop()
        expr_type = self.type_stack.pop()

        self.cube.check_assign(var_info.var_type, expr_type)

        self.quadruples.append(Quadruple('=', expr_res, None, var_name))

    # =============== PRINT ===============
    # printStmt : PRINT LPAREN printArgList? RPAREN SEMI
    def exitPrintStmt(self, ctx:PatitoParser.PrintStmtContext):
        if ctx.printArgList():
            # vienen n expresiones, están en la pila en orden de evaluación
            n = len(ctx.printArgList().expr())
            for _ in range(n):
                val = self.operand_stack.pop()
                self.type_stack.pop()
                self.quadruples.append(Quadruple('PRINT', val, None, None))
        else:
            self.quadruples.append(Quadruple('PRINT', None, None, None))