# Para proyecto: Scanner and Parser

## Lineas para la compilación del programa

1. java -jar jflex-full-1.9.1.jar Scanner.flex

2. java -jar java-cup-11b.jar -parser Parser -symbols sym Parser.cup

3. javac -cp ".:java-cup-11b.jar" \*.java

4. java -cp ".:java-cup-11b.jar" Main test.txt
