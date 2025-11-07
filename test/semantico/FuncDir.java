package semantico;
import java.util.*;

public final class FuncDir {
    private final Map<String, FuncInfo> funcs = new LinkedHashMap<>();

    /** Declara función (o "global"/"main"). */
    public void addFunction(String name, String tipoRet) {
        if (funcs.containsKey(name))
            throw new RuntimeException("Error semántico: función doblemente declarada: " + name);
        funcs.put(name, new FuncInfo(tipoRet));
    }

    public FuncInfo getFunc(String name) { return funcs.get(name); }

    /** Acceso directo a la tabla de variables de una función. */
    public VarTable getVarTable(String funcName) {
        FuncInfo fi = funcs.get(funcName);
        if (fi == null) throw new RuntimeException("Función no existe: " + funcName);
        return fi.getVarTable();
    }

    /** Registra un tipo de parámetro en la función actual (también lo puedes usar para chequeo posterior). */
    public void addParam(String funcName, String tipo) {
        FuncInfo fi = funcs.get(funcName);
        if (fi == null) throw new RuntimeException("Función no existe: " + funcName);
        fi.getParams().add(tipo);
    }

    /**
     * Búsqueda de variable con alcance: primero en la función actual,
     * si no, cae a "global". Devuelve null si no existe.
     */
    public VarInfo lookupVariable(String id, String currentFunction) {
        // Local de la función actual
        FuncInfo cur = funcs.get(currentFunction);
        if (cur != null) {
            VarInfo v = cur.getVarTable().lookup(id);
            if (v != null) return v;
        }
        // Global
        FuncInfo gl = funcs.get("global");
        if (gl != null) {
            VarInfo v = gl.getVarTable().lookup(id);
            if (v != null) return v;
        }
        return null;
    }

    /** Impresión sencilla del directorio para depuración (el Parser.cup la llama al final). */
    public void printDir() {
        System.out.println("===== FuncDir =====");
        for (Map.Entry<String, FuncInfo> e : funcs.entrySet()) {
            String fname = e.getKey();
            FuncInfo fi = e.getValue();
            System.out.print(fname + " -> { ret=" + fi.getTipo()
                + ", params=" + fi.getParams()
                + ", vars=" + fi.getVarTable().snapshot() + " }");
            System.out.println();
        }
        System.out.println("===================");
    }
}