from typing import Callable, Dict, List, Optional

from execution_memory import ExecutionMemory
from opcodes import OPCODES


OPCODE_NAMES = {v: k for k, v in OPCODES.items()}


class VirtualMachine:
    """
    Ejecuta cuádruplos simples usando el mapa de memoria definido.
    Dentro de esta entrega soporta expresiones, asignaciones, saltos y print.
    """

    def __init__(self, quadruples: List, constants: Optional[Dict[int, object]] = None):
        self.quadruples = quadruples
        self.ip = 0
        self.memory = ExecutionMemory(constants or {})
        self.memory.push_activation("main")
        self.return_ips: List[int] = []

        self.binary_ops: Dict[int, Callable] = {
            OPCODES["+"]: lambda a, b: a + b,
            OPCODES["-"]: lambda a, b: a - b,
            OPCODES["*"]: lambda a, b: a * b,
            OPCODES["/"]: lambda a, b: a / b,
            OPCODES["%"]: lambda a, b: a % b,
            OPCODES[">"]: lambda a, b: a > b,
            OPCODES["<"]: lambda a, b: a < b,
            OPCODES["!="]: lambda a, b: a != b,
            OPCODES["=="]: lambda a, b: a == b,
        }

    def run(self):
        while self.ip < len(self.quadruples):
            quad = self.quadruples[self.ip]
            jump_target = self._execute_quad(quad)
            if jump_target is None:
                self.ip += 1
            else:
                self.ip = jump_target

    # ------------------------------------------------------------
    # Ejecucion de instrucciones
    # ------------------------------------------------------------
    def _execute_quad(self, quad):
        op = quad.op

        if op in self.binary_ops:
            return self._binary_op(quad)

        if op == OPCODES["="]:
            return self._assign(quad)

        if op == OPCODES["GOTO"]:
            return quad.res

        if op == OPCODES["GOTOF"]:
            cond = self.memory.load(quad.left)
            return quad.res if not cond else None

        if op == OPCODES["PRINT"]:
            value = None if quad.left is None else self.memory.load(quad.left)
            print(value if value is not None else "")
            return None

        if op == OPCODES["ERA"]:
            return self._era(quad)

        if op == OPCODES["PARAM"]:
            return self._param(quad)

        if op == OPCODES["GOSUB"]:
            return self._gosub(quad)

        if op == OPCODES["RET"]:
            return self._ret()

        if op == OPCODES["ENDFUNC"]:
            return self._endfunc()

        raise NotImplementedError(f"Opcode no soportado: {OPCODE_NAMES.get(op, op)}")

    def _binary_op(self, quad):
        # Evalúa operaciones aritméticas/relacionales binarias
        left = self.memory.load(quad.left)
        right = self.memory.load(quad.right)
        result = self.binary_ops[quad.op](left, right)
        self.memory.store(quad.res, result)
        return None

    def _assign(self, quad):
        value = self.memory.load(quad.left)
        self.memory.store(quad.res, value)
        return None

    def _era(self, quad):
        # Prepara un nuevo marco para la llamada
        tag = quad.res if quad.res is not None else "call"
        self.memory.prepare_activation(str(tag))
        return None

    def _param(self, quad):
        # Carga el argumento a la activación pendiente
        value = self.memory.load(quad.left)
        self.memory.store_pending(quad.res, value)
        return None

    def _gosub(self, quad):
        self.return_ips.append(self.ip + 1)
        self.memory.push_prepared_activation()
        return quad.res

    def _ret(self):
        if not self.return_ips:
            raise RuntimeError("RET sin direccion de retorno")
        target = self.return_ips.pop()
        self.memory.pop_activation()
        return target

    def _endfunc(self):
        if not self.return_ips:
            raise RuntimeError("ENDFUNC sin direccion de retorno")
        target = self.return_ips.pop()
        self.memory.pop_activation()
        return target
