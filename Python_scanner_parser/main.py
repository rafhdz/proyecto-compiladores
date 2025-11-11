import sys
from antlr4 import *
from PatitoLexer import PatitoLexer
from PatitoParser import PatitoParser
from PatitoSemanticListener import PatitoSemanticListener
from antlr4.error.ErrorListener import ErrorListener
from semantics import SemanticError

class PatitoErrorListener(ErrorListener):
    def __init__(self):
        super().__init__()
        self.errors = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        self.errors.append(f"[Sintaxis] línea {line}:{column} → {msg}")

def main():
    if len(sys.argv) < 2:
        print("Uso: python main.py archivo.patito")
        return

    input_stream = FileStream(sys.argv[1], encoding='utf-8')

    lexer = PatitoLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = PatitoParser(token_stream)

    # sintaxis
    syn_err = PatitoErrorListener()
    parser.removeErrorListeners()
    parser.addErrorListener(syn_err)

    tree = parser.program()

    # si hay errores de sintaxis, los mostramos 
    if syn_err.errors:
        print("Errores de sintaxis:")
        for e in syn_err.errors:
            print("  ", e)
    # continuar con semántica para verificar funcionalidad

    # semántica
    sem_listener = PatitoSemanticListener()
    walker = ParseTreeWalker()
    try:
        walker.walk(sem_listener, tree)
        print("Análisis sintáctico y semántico completado.")
    except SemanticError as se:
        print(" Error semántico:", se)

if __name__ == "__main__":
    main()