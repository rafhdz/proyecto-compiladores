SEGMENT_SIZE = 1000

# Mapa fijo de segmentos de direcciones virtuales. Cada segmento
# mantiene 1000 direcciones consecutivas para un tipo/ámbito.
SEGMENT_LAYOUT = {
    # Globales
    "glob_int": (1000, SEGMENT_SIZE),
    "glob_float": (2000, SEGMENT_SIZE),
    "glob_bool": (3000, SEGMENT_SIZE),

    # Locales (por activación)
    "loc_int": (4000, SEGMENT_SIZE),
    "loc_float": (5000, SEGMENT_SIZE),
    "loc_bool": (6000, SEGMENT_SIZE),

    # Constantes
    "const_int": (7000, SEGMENT_SIZE),
    "const_float": (8000, SEGMENT_SIZE),
    "const_string": (9000, SEGMENT_SIZE),

    # Temporales (por activación)
    "temp_int": (10000, SEGMENT_SIZE),
    "temp_float": (11000, SEGMENT_SIZE),
    "temp_bool": (12000, SEGMENT_SIZE),
}


class MemorySegment:
    def __init__(self, name, start, size=SEGMENT_SIZE):
        self.name = name
        self.start = start
        self.size = size
        self.limit = start + size
        self.next = start

    def alloc(self):
        if self.next >= self.limit:
            raise MemoryError(f"Segmento {self.name} agotado (limite {self.limit - 1})")
        addr = self.next
        self.next += 1
        return addr


class VirtualMemory:
    def __init__(self):
        for name, (start, size) in SEGMENT_LAYOUT.items():
            setattr(self, name, MemorySegment(name, start, size))

    def alloc_var(self, scope, vtype):
        return getattr(self, f"{scope}_{vtype}").alloc()

    def alloc_const(self, vtype):
        return getattr(self, f"const_{vtype}").alloc()

    def alloc_temp(self, vtype):
        return getattr(self, f"temp_{vtype}").alloc()

    def layout(self):
        """
        Devuelve el mapa de segmentos para ser reutilizado por la
        Máquina Virtual en tiempo de ejecución.
        """
        return SEGMENT_LAYOUT.copy()
    
