package semantico;
import java.util.*;

public final class VarTable {
    private final Map<String, VarInfo> table = new LinkedHashMap<>();

    public void addVariable(String name, String tipo) {
        if (table.containsKey(name))
            throw new RuntimeException("Error semántico: variable doblemente declarada: " + name);
        table.put(name, new VarInfo(tipo));
    }

    public VarInfo lookup(String name) { return table.get(name); }

    /** Vista inmutable útil para imprimir el directorio. */
    public Map<String, VarInfo> snapshot() { return Collections.unmodifiableMap(table); }
}