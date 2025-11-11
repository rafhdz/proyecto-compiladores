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



del PatitoParser