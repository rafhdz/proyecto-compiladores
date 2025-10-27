import java.io.FileReader;
import java.io.Reader;
import java_cup.runtime.Symbol;

public class Main {
    public static void main(String[] args) {
        if (args.length < 1) {
            System.err.println("Error: Debe proporcionar un archivo de entrada.");
            System.err.println("Uso: java Main <archivo_fuente>");
            return;
        }

        String filePath = args[0];

        try (Reader reader = new FileReader(filePath)) {
            // 1. Crear el Scanner (Lexer)
            Scanner scanner = new Scanner(reader);
            
            // 2. Crear el Parser
            Parser parser = new Parser(scanner);
            
            // 3. Iniciar el análisis sintáctico
            // parser.parse() o parser.debug_parse() para depurar
            System.out.println("Iniciando análisis de: " + filePath);
            parser.do_parse();
            
            System.out.println("Análisis finalizado.");

        } catch (java.io.FileNotFoundException e) {
            System.err.println("Error: Archivo no encontrado '" + filePath + "'");
        } catch (java.io.IOException e) {
            System.err.println("Error de E/S al leer el archivo: " + e.getMessage());
        } catch (Exception e) {
            System.err.println("Error durante el análisis: " + e.getMessage());
            // e.printStackTrace(); // Descomentar para ver la traza completa
        }
    }
}