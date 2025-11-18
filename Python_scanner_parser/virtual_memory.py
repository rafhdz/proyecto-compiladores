class MemorySegment:
    def __init__(self, start):
        self.next = start

    def alloc(self):
        addr = self.next
        self.next += 1
        return addr


class VirtualMemory:

    def __init__(self):
        # Globales
        self.glob_int   = MemorySegment(1000)
        self.glob_float = MemorySegment(2000)
        self.glob_bool  = MemorySegment(3000)

        # Locales
        self.loc_int    = MemorySegment(4000)
        self.loc_float  = MemorySegment(5000)
        self.loc_bool   = MemorySegment(6000)

        # Constantes
        self.const_int    = MemorySegment(7000)
        self.const_float  = MemorySegment(8000)
        self.const_string = MemorySegment(9000)

        # Temporales
        self.temp_int     = MemorySegment(10000)
        self.temp_float   = MemorySegment(11000)
        self.temp_bool    = MemorySegment(12000)

    def alloc_var(self, scope, vtype):
        return getattr(self, f"{scope}_{vtype}").alloc()

    def alloc_const(self, vtype):
        return getattr(self, f"const_{vtype}").alloc()

    def alloc_temp(self, vtype):
        return getattr(self, f"temp_{vtype}").alloc()
    