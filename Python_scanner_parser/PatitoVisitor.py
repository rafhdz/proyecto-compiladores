# Generated from Patito.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .PatitoParser import PatitoParser
else:
    from PatitoParser import PatitoParser

# This class defines a complete generic visitor for a parse tree produced by PatitoParser.

class PatitoVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by PatitoParser#program.
    def visitProgram(self, ctx:PatitoParser.ProgramContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PatitoParser#globalVarSection.
    def visitGlobalVarSection(self, ctx:PatitoParser.GlobalVarSectionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PatitoParser#varDecl.
    def visitVarDecl(self, ctx:PatitoParser.VarDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PatitoParser#idList.
    def visitIdList(self, ctx:PatitoParser.IdListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PatitoParser#functionSection.
    def visitFunctionSection(self, ctx:PatitoParser.FunctionSectionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PatitoParser#funcDecl.
    def visitFuncDecl(self, ctx:PatitoParser.FuncDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PatitoParser#funcVarSection.
    def visitFuncVarSection(self, ctx:PatitoParser.FuncVarSectionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PatitoParser#paramList.
    def visitParamList(self, ctx:PatitoParser.ParamListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PatitoParser#param.
    def visitParam(self, ctx:PatitoParser.ParamContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PatitoParser#type.
    def visitType(self, ctx:PatitoParser.TypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PatitoParser#block.
    def visitBlock(self, ctx:PatitoParser.BlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PatitoParser#stmt.
    def visitStmt(self, ctx:PatitoParser.StmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PatitoParser#assignStmt.
    def visitAssignStmt(self, ctx:PatitoParser.AssignStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PatitoParser#ifStmt.
    def visitIfStmt(self, ctx:PatitoParser.IfStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PatitoParser#whileStmt.
    def visitWhileStmt(self, ctx:PatitoParser.WhileStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PatitoParser#printStmt.
    def visitPrintStmt(self, ctx:PatitoParser.PrintStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PatitoParser#printArgList.
    def visitPrintArgList(self, ctx:PatitoParser.PrintArgListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PatitoParser#funcCallStmt.
    def visitFuncCallStmt(self, ctx:PatitoParser.FuncCallStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PatitoParser#funcCall.
    def visitFuncCall(self, ctx:PatitoParser.FuncCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PatitoParser#argList.
    def visitArgList(self, ctx:PatitoParser.ArgListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PatitoParser#toAdd.
    def visitToAdd(self, ctx:PatitoParser.ToAddContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PatitoParser#relExpr.
    def visitRelExpr(self, ctx:PatitoParser.RelExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PatitoParser#relop.
    def visitRelop(self, ctx:PatitoParser.RelopContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PatitoParser#addOp.
    def visitAddOp(self, ctx:PatitoParser.AddOpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PatitoParser#toMult.
    def visitToMult(self, ctx:PatitoParser.ToMultContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PatitoParser#multOp.
    def visitMultOp(self, ctx:PatitoParser.MultOpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PatitoParser#toUnary.
    def visitToUnary(self, ctx:PatitoParser.ToUnaryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PatitoParser#unarySign.
    def visitUnarySign(self, ctx:PatitoParser.UnarySignContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PatitoParser#toAtom.
    def visitToAtom(self, ctx:PatitoParser.ToAtomContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by PatitoParser#atom.
    def visitAtom(self, ctx:PatitoParser.AtomContext):
        return self.visitChildren(ctx)



del PatitoParser