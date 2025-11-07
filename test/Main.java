import java.io.*;
import java_cup.runtime.*;
import semantico.*;

public class Main {
    public static void main(String[] args) throws Exception {
        // Si no se pasa archivo, usa uno por defecto
        String filename = (args.length > 0) ? args[0] : "programa.txt";
        System.out.println("Analizando archivo: " + filename);

        FileReader fr = new FileReader(filename);
        Scanner scanner = new Scanner(fr);   // Tu scanner.flex generado
        Parser parser = new Parser(scanner); // Tu parser.cup generado

        try {
            parser.parse();  // Ejecuta el análisis
            System.out.println("\nAnálisis completo sin errores.");
        } catch (Exception e) {
            System.err.println("\nError durante el análisis:");
            e.printStackTrace();
        }
        // Mostrar directorio de funciones después del parseo
        try {
            // Intentamos acceder al campo funcDir del parser (ya que el Parser.cup lo tiene público)
            java.lang.reflect.Field f = Parser.class.getDeclaredField("funcDir");
            f.setAccessible(true);
            Object fd = f.get(parser);
            if (fd instanceof semantico.FuncDir) {
                System.out.println("\n===== Estado Semántico =====");
                ((semantico.FuncDir) fd).printDir();
            }
        } catch (Exception ignore) { }
    }
}