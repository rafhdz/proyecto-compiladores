package semantico;
import java.util.*;

/** Cubo simple y explícito (strings "int"/"float") compatible con Parser.cup */
public final class CuboSemantico {
    private static final Set<String> NUM = Set.of("int", "float");
    private static final Set<String> ARIT = Set.of("+","-","*","/");
    private static final Set<String> REL  = Set.of(">","<","!=");

    /** Devuelve tipo resultante o "ERROR". Para relacionales regresamos "int" (booleana entera). */
    public String checkOperation(String op, String t1, String t2) {
        // Operaciones aritméticas
        if (ARIT.contains(op)) {
            if (!NUM.contains(t1) || !NUM.contains(t2)) return "ERROR";
            return (t1.equals("float") || t2.equals("float")) ? "float" : "int";
        }
        // Operaciones relacionales
        if (REL.contains(op)) {
            if (!NUM.contains(t1) || !NUM.contains(t2)) return "ERROR";
            return "int"; // booleano como entero (compatible con tu gramática actual)
        }
        return "ERROR";
    }

    /** Asignación: mismo tipo, o "float = int" (widening). */
    public String checkAssignment(String target, String expr) {
        if (target.equals(expr)) return target;
        if (target.equals("float") && expr.equals("int")) return "float";
        return "ERROR";
    }
}