# PatitoSemanticListener.py

from PatitoListener import PatitoListener
from PatitoParser import PatitoParser
from semantics import FuncDir, VarTableHelper, SemanticCube, SemanticError

class PatitoSemanticListener(PatitoListener):
    def __init__(self):
        # estructuras principales
        self.funcdir = FuncDir()
        self.vartab = VarTableHelper(self.funcdir)
        self.cube = SemanticCube()

        # pila de tipos para expresiones
        self.type_stack = []

    # ========== PROGRAM Y SCOPES ==========

    def enterProgram(self, ctx:PatitoParser.ProgramContext):
        # ya tenemos "global"
        pass

    # global vars: varDecl+
    def enterVarDecl(self, ctx:PatitoParser.VarDeclContext):
        # lista de IDs y tipo al final
        var_type = ctx.type_().getText()
        ids = [idtok.getText() for idtok in ctx.idList().ID()]
        for name in ids:
            self.vartab.add_var(name, var_type)

    # funciones
    def enterFuncDecl(self, ctx:PatitoParser.FuncDeclContext):
        ret_type = ctx.type_().getText()
        func_name = ctx.ID().getText()
        # registrar función
        self.funcdir.add_function(func_name, ret_type)

        # parámetros si hay
        if ctx.paramList():
            for p in ctx.paramList().param():
                pname = p.ID().getText()
                ptype = p.type_().getText()
                self.funcdir.add_param(pname, ptype)

        # vars locales si hay (se declaran dentro del mismo scope)
        if ctx.funcVarSection():
            for v in ctx.funcVarSection().varDecl():
                vtype = v.type_().getText()
                ids = [idtok.getText() for idtok in v.idList().ID()]
                for name in ids:
                    self.vartab.add_var(name, vtype)

    def exitFuncDecl(self, ctx:PatitoParser.FuncDeclContext):
        # regresamos al global cuando termina
        self.funcdir.set_global()

    # main se trata como un función tipo void main
    def enterBlock(self, ctx:PatitoParser.BlockContext):
        pass

    # ========== ASIGNACIONES ==========

    def exitAssignStmt(self, ctx:PatitoParser.AssignStmtContext):
        var_name = ctx.ID().getText()
        var_info = self.vartab.lookup(var_name)
        # el tipo de la expresión es el tope de la pila
        expr_type = self.type_stack.pop()
        self.cube.check_assign(var_info.var_type, expr_type)

    # ========== EXPRESIONES ==========

    # atom: ID | CTE_INT | CTE_FLOAT | STRING | ...
    def exitAtom(self, ctx:PatitoParser.AtomContext):
        if ctx.ID():
            name = ctx.ID().getText()
            vinfo = self.vartab.lookup(name)
            self.type_stack.append(vinfo.var_type)
        elif ctx.CTE_INT():
            self.type_stack.append('int')
        elif ctx.CTE_FLOAT():
            self.type_stack.append('float')
        elif ctx.STRING():
            self.type_stack.append('string')
        elif ctx.funcCall():
            self.type_stack.append('void')
        else:
            pass

    # multExpr: multExpr (* /) unaryExpr
    def exitMultOp(self, ctx:PatitoParser.MultOpContext):
        right = self.type_stack.pop()
        left = self.type_stack.pop()
        op = ctx.getChild(1).getText()   # '*' o '/'
        res_t = self.cube.check_op(op, left, right)
        self.type_stack.append(res_t)

    # addExpr: addExpr (+ -) multExpr
    def exitAddOp(self, ctx:PatitoParser.AddOpContext):
        right = self.type_stack.pop()
        left = self.type_stack.pop()
        op = ctx.getChild(1).getText()   # '+' o '-'
        res_t = self.cube.check_op(op, left, right)
        self.type_stack.append(res_t)

    # expr 
    def exitRelExpr(self, ctx:PatitoParser.RelExprContext):
        right = self.type_stack.pop()
        left = self.type_stack.pop()
        op = ctx.relop().getText()
        res_t = self.cube.check_op(op, left, right)
        self.type_stack.append(res_t)

    # unary: (-) unary
    def exitUnarySign(self, ctx:PatitoParser.UnarySignContext):
        # unario conserva el tipo del operando
        # solo comprobamos que sea numérico
        t = self.type_stack.pop()
        if t not in ('int', 'float'):
            raise SemanticError(f"Operador unario aplicado a tipo no numérico: {t}")
        self.type_stack.append(t)