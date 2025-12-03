class VarInfo:
    # Contenedor simple para metadatos de una variable
    def __init__(self, name, var_type, address):
        self.name = name
        self.var_type = var_type
        self.address = address

    def __repr__(self):
        return f"VarInfo(name={self.name}, type={self.var_type}, addr={self.address})"
