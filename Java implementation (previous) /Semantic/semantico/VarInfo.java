package semantico;

public final class VarInfo {
    private final String tipo;
    public VarInfo(String tipo) { this.tipo = tipo; }
    public String getTipo() { return tipo; }
    @Override public String toString() { return "{ tipo=" + tipo + " }"; }
}