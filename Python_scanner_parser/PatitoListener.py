# Generated from Patito.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .PatitoParser import PatitoParser
else:
    from PatitoParser import PatitoParser

# This class defines a complete listener for a parse tree produced by PatitoParser.
class PatitoListener(ParseTreeListener):

    # Enter a parse tree produced by PatitoParser#program.
    def enterProgram(self, ctx:PatitoParser.ProgramContext):
        pass

    # Exit a parse tree produced by PatitoParser#program.
    def exitProgram(self, ctx:PatitoParser.ProgramContext):
        pass


    # Enter a parse tree produced by PatitoParser#globalVarSection.
    def enterGlobalVarSection(self, ctx:PatitoParser.GlobalVarSectionContext):
        pass

    # Exit a parse tree produced by PatitoParser#globalVarSection.
    def exitGlobalVarSection(self, ctx:PatitoParser.GlobalVarSectionContext):
        pass


    # Enter a parse tree produced by PatitoParser#varDecl.
    def enterVarDecl(self, ctx:PatitoParser.VarDeclContext):
        pass

    # Exit a parse tree produced by PatitoParser#varDecl.
    def exitVarDecl(self, ctx:PatitoParser.VarDeclContext):
        pass


    # Enter a parse tree produced by PatitoParser#idList.
    def enterIdList(self, ctx:PatitoParser.IdListContext):
        pass

    # Exit a parse tree produced by PatitoParser#idList.
    def exitIdList(self, ctx:PatitoParser.IdListContext):
        pass


    # Enter a parse tree produced by PatitoParser#functionSection.
    def enterFunctionSection(self, ctx:PatitoParser.FunctionSectionContext):
        pass

    # Exit a parse tree produced by PatitoParser#functionSection.
    def exitFunctionSection(self, ctx:PatitoParser.FunctionSectionContext):
        pass


    # Enter a parse tree produced by PatitoParser#funcDecl.
    def enterFuncDecl(self, ctx:PatitoParser.FuncDeclContext):
        pass

    # Exit a parse tree produced by PatitoParser#funcDecl.
    def exitFuncDecl(self, ctx:PatitoParser.FuncDeclContext):
        pass


    # Enter a parse tree produced by PatitoParser#funcVarSection.
    def enterFuncVarSection(self, ctx:PatitoParser.FuncVarSectionContext):
        pass

    # Exit a parse tree produced by PatitoParser#funcVarSection.
    def exitFuncVarSection(self, ctx:PatitoParser.FuncVarSectionContext):
        pass


    # Enter a parse tree produced by PatitoParser#paramList.
    def enterParamList(self, ctx:PatitoParser.ParamListContext):
        pass

    # Exit a parse tree produced by PatitoParser#paramList.
    def exitParamList(self, ctx:PatitoParser.ParamListContext):
        pass


    # Enter a parse tree produced by PatitoParser#param.
    def enterParam(self, ctx:PatitoParser.ParamContext):
        pass

    # Exit a parse tree produced by PatitoParser#param.
    def exitParam(self, ctx:PatitoParser.ParamContext):
        pass


    # Enter a parse tree produced by PatitoParser#type.
    def enterType(self, ctx:PatitoParser.TypeContext):
        pass

    # Exit a parse tree produced by PatitoParser#type.
    def exitType(self, ctx:PatitoParser.TypeContext):
        pass


    # Enter a parse tree produced by PatitoParser#block.
    def enterBlock(self, ctx:PatitoParser.BlockContext):
        pass

    # Exit a parse tree produced by PatitoParser#block.
    def exitBlock(self, ctx:PatitoParser.BlockContext):
        pass


    # Enter a parse tree produced by PatitoParser#stmt.
    def enterStmt(self, ctx:PatitoParser.StmtContext):
        pass

    # Exit a parse tree produced by PatitoParser#stmt.
    def exitStmt(self, ctx:PatitoParser.StmtContext):
        pass


    # Enter a parse tree produced by PatitoParser#assignStmt.
    def enterAssignStmt(self, ctx:PatitoParser.AssignStmtContext):
        pass

    # Exit a parse tree produced by PatitoParser#assignStmt.
    def exitAssignStmt(self, ctx:PatitoParser.AssignStmtContext):
        pass


    # Enter a parse tree produced by PatitoParser#ifStmt.
    def enterIfStmt(self, ctx:PatitoParser.IfStmtContext):
        pass

    # Exit a parse tree produced by PatitoParser#ifStmt.
    def exitIfStmt(self, ctx:PatitoParser.IfStmtContext):
        pass


    # Enter a parse tree produced by PatitoParser#whileStmt.
    def enterWhileStmt(self, ctx:PatitoParser.WhileStmtContext):
        pass

    # Exit a parse tree produced by PatitoParser#whileStmt.
    def exitWhileStmt(self, ctx:PatitoParser.WhileStmtContext):
        pass


    # Enter a parse tree produced by PatitoParser#printStmt.
    def enterPrintStmt(self, ctx:PatitoParser.PrintStmtContext):
        pass

    # Exit a parse tree produced by PatitoParser#printStmt.
    def exitPrintStmt(self, ctx:PatitoParser.PrintStmtContext):
        pass


    # Enter a parse tree produced by PatitoParser#printArgList.
    def enterPrintArgList(self, ctx:PatitoParser.PrintArgListContext):
        pass

    # Exit a parse tree produced by PatitoParser#printArgList.
    def exitPrintArgList(self, ctx:PatitoParser.PrintArgListContext):
        pass


    # Enter a parse tree produced by PatitoParser#funcCallStmt.
    def enterFuncCallStmt(self, ctx:PatitoParser.FuncCallStmtContext):
        pass

    # Exit a parse tree produced by PatitoParser#funcCallStmt.
    def exitFuncCallStmt(self, ctx:PatitoParser.FuncCallStmtContext):
        pass


    # Enter a parse tree produced by PatitoParser#funcCall.
    def enterFuncCall(self, ctx:PatitoParser.FuncCallContext):
        pass

    # Exit a parse tree produced by PatitoParser#funcCall.
    def exitFuncCall(self, ctx:PatitoParser.FuncCallContext):
        pass


    # Enter a parse tree produced by PatitoParser#argList.
    def enterArgList(self, ctx:PatitoParser.ArgListContext):
        pass

    # Exit a parse tree produced by PatitoParser#argList.
    def exitArgList(self, ctx:PatitoParser.ArgListContext):
        pass


    # Enter a parse tree produced by PatitoParser#toAdd.
    def enterToAdd(self, ctx:PatitoParser.ToAddContext):
        pass

    # Exit a parse tree produced by PatitoParser#toAdd.
    def exitToAdd(self, ctx:PatitoParser.ToAddContext):
        pass


    # Enter a parse tree produced by PatitoParser#relExpr.
    def enterRelExpr(self, ctx:PatitoParser.RelExprContext):
        pass

    # Exit a parse tree produced by PatitoParser#relExpr.
    def exitRelExpr(self, ctx:PatitoParser.RelExprContext):
        pass


    # Enter a parse tree produced by PatitoParser#relop.
    def enterRelop(self, ctx:PatitoParser.RelopContext):
        pass

    # Exit a parse tree produced by PatitoParser#relop.
    def exitRelop(self, ctx:PatitoParser.RelopContext):
        pass


    # Enter a parse tree produced by PatitoParser#addOp.
    def enterAddOp(self, ctx:PatitoParser.AddOpContext):
        pass

    # Exit a parse tree produced by PatitoParser#addOp.
    def exitAddOp(self, ctx:PatitoParser.AddOpContext):
        pass


    # Enter a parse tree produced by PatitoParser#toMult.
    def enterToMult(self, ctx:PatitoParser.ToMultContext):
        pass

    # Exit a parse tree produced by PatitoParser#toMult.
    def exitToMult(self, ctx:PatitoParser.ToMultContext):
        pass


    # Enter a parse tree produced by PatitoParser#multOp.
    def enterMultOp(self, ctx:PatitoParser.MultOpContext):
        pass

    # Exit a parse tree produced by PatitoParser#multOp.
    def exitMultOp(self, ctx:PatitoParser.MultOpContext):
        pass


    # Enter a parse tree produced by PatitoParser#toUnary.
    def enterToUnary(self, ctx:PatitoParser.ToUnaryContext):
        pass

    # Exit a parse tree produced by PatitoParser#toUnary.
    def exitToUnary(self, ctx:PatitoParser.ToUnaryContext):
        pass


    # Enter a parse tree produced by PatitoParser#unarySign.
    def enterUnarySign(self, ctx:PatitoParser.UnarySignContext):
        pass

    # Exit a parse tree produced by PatitoParser#unarySign.
    def exitUnarySign(self, ctx:PatitoParser.UnarySignContext):
        pass


    # Enter a parse tree produced by PatitoParser#toAtom.
    def enterToAtom(self, ctx:PatitoParser.ToAtomContext):
        pass

    # Exit a parse tree produced by PatitoParser#toAtom.
    def exitToAtom(self, ctx:PatitoParser.ToAtomContext):
        pass


    # Enter a parse tree produced by PatitoParser#atom.
    def enterAtom(self, ctx:PatitoParser.AtomContext):
        pass

    # Exit a parse tree produced by PatitoParser#atom.
    def exitAtom(self, ctx:PatitoParser.AtomContext):
        pass


    # Enter a parse tree produced by PatitoParser#returnStmt.
    def enterReturnStmt(self, ctx:PatitoParser.ReturnStmtContext):
        pass

    # Exit a parse tree produced by PatitoParser#returnStmt.
    def exitReturnStmt(self, ctx:PatitoParser.ReturnStmtContext):
        pass



del PatitoParser