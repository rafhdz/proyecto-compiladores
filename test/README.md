### Lineas para ejecutar el programa

1. rm -f Parser.java sym.java Scanner.java _.class semantico/_.class 2>/dev/null
2. java -jar jflex-full-1.9.1.jar Scanner.flex
3. java -jar java-cup-11b.jar -parser Parser -symbols sym Parser.cup
4. javac -cp .:java-cup-11b.jar:jflex-full-1.9.1.jar semantico/_.java _.java
5. java -cp .:java-cup-11b.jar:jflex-full-1.9.1.jar:. Main programa.txt
