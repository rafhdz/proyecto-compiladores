from PatitoListener import PatitoListener
from PatitoParser import PatitoParser
from FuncDir import FuncDir
from VarTableHelper import VarTableHelper
from semantics import SemanticCube
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

        self.constants = {}  # valor hacia dirección

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

    # ============================================================
    # CONSTANTES
    # ============================================================
    def get_or_add_constant(self, value, vtype):
        if value in self.constants:
            return self.constants[value]

        addr = self.memory.alloc_const(vtype)
        self.constants[value] = addr
        return addr

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

        if ctx.paramList():
            for p in ctx.paramList().param():
                self.funcdir.add_param(
                    p.ID().getText(),
                    p.type_().getText()
                )

        if ctx.funcVarSection():
            for v in ctx.funcVarSection().varDecl():
                vtype = v.type_().getText()
                for name in [x.getText() for x in v.idList().ID()]:
                    self.vartab.add_var(name, vtype)

    def exitFuncDecl(self, ctx):
        self.funcdir.set_global()

    # ============================================================
    # ÁTOMOS
    # ============================================================
    def exitAtom(self, ctx):
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
        r_op = self.operand_stack.pop()
        r_ty = self.type_stack.pop()
        l_op = self.operand_stack.pop()
        l_ty = self.type_stack.pop()

        op = ctx.relop().getText()
        res_ty = self.cube.check_op(op, l_ty, r_ty)

        _, addr = self.temp_manager.new_temp(res_ty)
        opcode = OPCODES[op]

        self.quadruples.append(Quadruple(opcode, l_op, r_op, addr))

        self.operand_stack.append(addr)
        self.type_stack.append(res_ty)

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

    # ============================================================
    # PRINT
    # ============================================================
    def exitPrintStmt(self, ctx):
        if ctx.printArgList():
            for _ in range(len(ctx.printArgList().expr())):
                addr = self.operand_stack.pop()
                self.type_stack.pop()
                self.quadruples.append(
                    Quadruple(OPCODES["PRINT"], addr, None, None)
                )
        else:
            self.quadruples.append(
                Quadruple(OPCODES["PRINT"], None, None, None)
            )

    # ============================================================
    # IF / ELSE
    # ============================================================
    def enterIfStmt(self, ctx):
        self.in_if_condition = True

    def exitIfStmt(self, ctx):
        pass

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