import java.io.*;
import java_cup.runtime.*;
import semantico.*;

public class Main {
    private static final String RESET = "\u001B[0m"; // Mejora visual de los errores 
    private static final String RED = "\u001B[31m";
    private static final String GREEN = "\u001B[32m";
    private static final String CYAN = "\u001B[36m";
    private static final String BOLD = "\u001B[1m";

    public static void main(String[] args) throws Exception {
        String filename = (args.length > 0) ? args[0] : "programa.txt";
        System.out.println(BOLD + CYAN + "\n📘 Analizando archivo: " + filename + RESET);

        FileReader fr = new FileReader(filename);
        Scanner scanner = new Scanner(fr);
        Parser parser = new Parser(scanner);

        // Capturar errores semánticos de System.err
        ByteArrayOutputStream errBuffer = new ByteArrayOutputStream();
        PrintStream originalErr = System.err;
        System.setErr(new PrintStream(errBuffer));

        boolean semanticErrors = false;

        try {
            parser.parse(); // ejecuta análisis

            // Restaurar System.err y obtener su contenido
            System.setErr(originalErr);
            String errorOutput = errBuffer.toString();

            if (!errorOutput.isEmpty()) {
                System.out.print(errorOutput); // volver a mostrarlo en consola
                if (errorOutput.contains("[Error semántico]")) {
                    semanticErrors = true;
                }
            }

            // Mostrar mensaje final correcto según tipo de error
            if (parser.syntaxError) {
                System.out.println(RED + "\n Análisis con errores sintácticos." + RESET);
            } else if (semanticErrors) {
                System.out.println(RED + "\n Análisis completado con errores semánticos." + RESET);
            } else {
                System.out.println(GREEN + "\n Análisis completado correctamente." + RESET);
            }

        } catch (Exception e) {
            System.setErr(originalErr);
            System.err.println(RED + "\n Error fatal durante el análisis." + RESET);
            e.printStackTrace();
        }
    }
}