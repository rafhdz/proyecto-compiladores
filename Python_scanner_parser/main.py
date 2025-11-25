import sys
from antlr4 import *
from PatitoLexer import PatitoLexer
from PatitoParser import PatitoParser
from PatitoSemanticListener import PatitoSemanticListener
from antlr4.error.ErrorListener import ErrorListener
from semantics import SemanticError
from virtual_machine import VirtualMachine
from opcodes import OPCODES

class PatitoErrorListener(ErrorListener):
    def __init__(self):
        super().__init__()
        self.errors = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        self.errors.append(f"[Sintaxis] línea {line}:{column} → {msg}")

def main():
    if len(sys.argv) < 2:
        print("Uso requerido: python main.py archivo_prueba.txt")
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

    # mostrar errores de sintaxis
    if syn_err.errors:
        print("Errores de sintaxis:")
        for e in syn_err.errors:
            print("  ", e)
        return

    # semántica
    sem_listener = PatitoSemanticListener()
    walker = ParseTreeWalker()
    try:
        walker.walk(sem_listener, tree)
        print("\n Análisis sintáctico y semántico completado.")
    except SemanticError as se:
        print("\n Error semántico:", se)
        return

    # Cuádruplos generados
    print("\n=== CUADRUPLOS GENERADOS ===")
    for i, q in enumerate(sem_listener.quadruples):
        print(f"{i:03}  {q}")

    # Cuádruplos amigables con nombres y opcodes
    print("\n=== CUADRUPLOS (para DEBUGING) ===")
    op_names = {v: k for k, v in OPCODES.items()}
    symbols = sem_listener.build_symbol_table()

    def pretty(addr):
        if addr is None:
            return None
        return symbols.get(addr, addr)

    for i, q in enumerate(sem_listener.quadruples):
        op = op_names.get(q.op, q.op)
        l = pretty(q.left)
        r = pretty(q.right)
        res = pretty(q.res)
        print(f"{i:03}  ({op}, {l}, {r}, {res})")

    # Ejecución en Máquina Virtual
    print("\n=== EJECUCIÓN EN MÁQUINA VIRTUAL ===")
    try:
        vm = VirtualMachine(sem_listener.quadruples, sem_listener.constants)
        vm.run()
    except Exception as exc:
        print(f"Fallo en ejecución de VM: {exc}")

if __name__ == "__main__":
    main()
