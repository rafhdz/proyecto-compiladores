package semantico;
import java.util.*;

public final class FuncInfo {
    private final String tipo;           // tipo de retorno
    private final List<String> params;   // tipos de parámetros, en orden
    private final VarTable vars;         // variables locales (y parámetros) de la función

    public FuncInfo(String tipoRet) {
        this.tipo = tipoRet;
        this.params = new ArrayList<>();
        this.vars = new VarTable();
    }

    // El Parser.cup llama a getTipo() en llamadas a función
    public String getTipo() { return tipo; }

    public List<String> getParams() { return params; }
    public VarTable getVarTable() { return vars; }
}