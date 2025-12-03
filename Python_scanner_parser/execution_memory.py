from typing import Dict, List, Optional

from virtual_memory import SEGMENT_LAYOUT


class MemoryWindow:
    """
    Ventana de direcciones contiguas asociada a un segmento del mapa de memoria.
    Guarda valores reales de ejecución (no solo las direcciones).
    """

    def __init__(self, name: str, start: int, size: int):
        self.name = name
        self.start = start
        self.end = start + size
        self._data: Dict[int, object] = {}

    def contains(self, addr: int) -> bool:
        return self.start <= addr < self.end

    def load(self, addr: int):
        if not self.contains(addr):
            raise ValueError(f"Direccion {addr} no pertenece al segmento {self.name}")
        if addr not in self._data:
            raise RuntimeError(f"Direccion {addr} no inicializada en {self.name}")
        return self._data[addr]

    def store(self, addr: int, value):
        if not self.contains(addr):
            raise ValueError(f"Direccion {addr} no pertenece al segmento {self.name}")
        self._data[addr] = value

    def snapshot(self):
        return dict(self._data)


class ActivationRecord:
    """
    Un marco de activacion contiene los segmentos locales y temporales de una llamada.
    """

    def __init__(self, tag: str = "anon"):
        self.tag = tag
        self.locals = {
            name: MemoryWindow(name, start, size)
            for name, (start, size) in SEGMENT_LAYOUT.items()
            if name.startswith("loc_")
        }
        self.temps = {
            name: MemoryWindow(name, start, size)
            for name, (start, size) in SEGMENT_LAYOUT.items()
            if name.startswith("temp_")
        }

    def windows(self) -> List[MemoryWindow]:
        return list(self.locals.values()) + list(self.temps.values())


class ExecutionMemory:
    """
    Memoria en tiempo de ejecucion que conoce el mapa completo y separa:
    - Segmentos globales (persisten toda la corrida)
    - Segmentos de constantes (solo lectura)
    - Segmentos locales/temporales por activacion de funcion
    """

    def __init__(self, constants: Optional[Dict[int, object]] = None):
        self.layout = SEGMENT_LAYOUT
        self.globals = {
            name: MemoryWindow(name, start, size)
            for name, (start, size) in self.layout.items()
            if name.startswith("glob_")
        }
        self.constants = {
            name: MemoryWindow(name, start, size)
            for name, (start, size) in self.layout.items()
            if name.startswith("const_")
        }
        self.call_stack: List[ActivationRecord] = []
        self.current_activation: Optional[ActivationRecord] = None
        self.pending_activation: Optional[ActivationRecord] = None

        if constants:
            self._load_constants(constants)

    # ------------------------------------------------------------
    # Manejo de activaciones
    # ------------------------------------------------------------
    def push_activation(self, tag: str = "call"):
        # Crea y activa un nuevo marco de ejecución (función)
        ar = ActivationRecord(tag)
        self.call_stack.append(ar)
        self.current_activation = ar
        return ar

    def prepare_activation(self, tag: str = "call"):
        # Reserva un marco antes de evaluarse los PARAM
        self.pending_activation = ActivationRecord(tag)
        return self.pending_activation

    def push_prepared_activation(self):
        if not self.pending_activation:
            raise RuntimeError("No hay activacion preparada para hacer push")
        self.call_stack.append(self.pending_activation)
        self.current_activation = self.pending_activation
        self.pending_activation = None
        return self.current_activation

    def pop_activation(self):
        if not self.call_stack:
            raise RuntimeError("Pila de activaciones vacia")
        self.call_stack.pop()
        self.current_activation = self.call_stack[-1] if self.call_stack else None

    # ------------------------------------------------------------
    # Lectura / escritura
    # ------------------------------------------------------------
    def load(self, addr: int):
        win = self._window_for_address(addr, allow_constants=True)
        if addr not in win._data:
            if win.name.startswith("const_"):
                raise RuntimeError(f"Direccion {addr} no inicializada en {win.name}")
            default = self._default_for_segment(win.name)
            win.store(addr, default)
        return win.load(addr)

    def store(self, addr: int, value):
        # Almacena solo en segmentos no constantes
        win = self._window_for_address(addr, allow_constants=False)
        win.store(addr, value)

    def store_pending(self, addr: int, value):
        if not self.pending_activation:
            raise RuntimeError("No hay activacion preparada para PARAM")
        win = self._window_for_address(
            addr, allow_constants=False, activation_override=self.pending_activation
        )
        win.store(addr, value)

    # ------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------
    def _window_for_address(
        self,
        addr: int,
        allow_constants: bool,
        activation_override: Optional[ActivationRecord] = None,
    ) -> MemoryWindow:
        search_order = []

        activation = activation_override or self.current_activation
        if activation:
            # Primero se buscan temporales y locales del marco activo
            search_order.extend(activation.windows())

        search_order.extend(self.globals.values())

        if allow_constants:
            search_order.extend(self.constants.values())

        for win in search_order:
            if win.contains(addr):
                return win

        raise RuntimeError(f"Direccion {addr} fuera del mapa de memoria")

    def _default_for_segment(self, segment_name: str):
        if segment_name.endswith("int"):
            return 0
        if segment_name.endswith("float"):
            return 0.0
        if segment_name.endswith("bool"):
            return False
        if segment_name.endswith("string"):
            return ""
        return None

    def _load_constants(self, constants: Dict[int, object]):
        """
        Recibe un diccionario direccion -> valor y los guarda en el segmento
        de constantes correspondiente.
        """
        for addr, value in constants.items():
            win = self._window_for_address(addr, allow_constants=True)
            if not win.name.startswith("const_"):
                raise RuntimeError(f"La direccion {addr} no pertenece al segmento de constantes")
            win.store(addr, value)

    def snapshot(self):
        """
        Regresa una fotografia ligera para debug. No se usa en ejecucion normal.
        """
        return {
            "globals": {k: v.snapshot() for k, v in self.globals.items()},
            "constants": {k: v.snapshot() for k, v in self.constants.items()},
            "activation": None
            if not self.current_activation
            else {
                "tag": self.current_activation.tag,
                "locals": {k: v.snapshot() for k, v in self.current_activation.locals.items()},
                "temps": {k: v.snapshot() for k, v in self.current_activation.temps.items()},
            },
        }
