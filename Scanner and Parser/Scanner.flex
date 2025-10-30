import java_cup.runtime.Symbol;

%%

%class Scanner
%public
%cup
%line
%column

%{
    /**
     * Símbolo de CUP con la información de línea y columna.
     */
    private Symbol symbol(int type) {
        return new Symbol(type, yyline + 1, yycolumn + 1);
    }

    /**
     * Símbolo de CUP con la información de línea, columna y un valor.
     */
    private Symbol symbol(int type, Object value) {
        return new Symbol(type, yyline + 1, yycolumn + 1, value);
    }
%}

/* Declaración de Estados */
%state COMMENT

/* Expresiones Regulares */

/* Espacios en blanco (se ignoran) */
WHITESPACE = [ \t\r\n]+

/* Comentario de línea (se ignora) */
LINE_COMMENT = \/\/[^\r\n]*

/* Identificador */
ID = [a-zA-Z][a-zA-Z0-9_]*

/* Constante Entera */
CTE_INT = [0-9]+

/* Constante Flotante */
CTE_FLOAT = [0-9]+\.[0-9]+

/* Constante de Cadena */
CTE_STRING = \"[^\"]*\"

%%

/* Reglas del léxico */

<YYINITIAL> {
    {WHITESPACE}    { /* Ignorar espacios en blanco */ }
    {LINE_COMMENT}  { /* Ignorar comentarios de línea */ }
    
    /* Inicio de comentario de bloque */
    "/*"            { yybegin(COMMENT); }

    /* Palabras Reservadas */
    "program"       { return symbol(sym.PROGRAM); }
    "main"          { return symbol(sym.MAIN); }
    "end"           { return symbol(sym.END); }
    "var"           { return symbol(sym.VAR); }
    "int"           { return symbol(sym.INT); }
    "float"         { return symbol(sym.FLOAT); }
    "void"          { return symbol(sym.VOID); }
    "if"            { return symbol(sym.IF); }
    "else"          { return symbol(sym.ELSE); }
    "while"         { return symbol(sym.WHILE); }
    "do"            { return symbol(sym.DO); }
    "print"         { return symbol(sym.PRINT); }

    /* Operadores */
    "="             { return symbol(sym.ASSIGN); }
    "+"             { return symbol(sym.PLUS); }
    "-"             { return symbol(sym.MINUS); }
    "*"             { return symbol(sym.TIMES); }
    "/"             { return symbol(sym.DIV); }
    ">"             { return symbol(sym.GT); }
    "<"             { return symbol(sym.LT); }
    "!="            { return symbol(sym.NE); }

    /* Puntuación y Agrupación */
    ";"             { return symbol(sym.SEMI); }
    ","             { return symbol(sym.COMMA); }
    ":"             { return symbol(sym.COLON); }
    "("             { return symbol(sym.LPAREN); }
    ")"             { return symbol(sym.RPAREN); }
    "{"             { return symbol(sym.LBRACE); }
    "}"             { return symbol(sym.RBRACE); }

    /* Constantes e Identificadores */
    /* El orden importa: Float debe ir antes que Int */
    
    {CTE_FLOAT}     { return symbol(sym.CTE_FLOAT, Float.parseFloat(yytext())); }
    
    {CTE_INT}       { return symbol(sym.CTE_INT, Integer.parseInt(yytext())); }
    
    {CTE_STRING}    { 
        /* Se eliminan las comillas dobles del valor */
        String val = yytext().substring(1, yytext().length() - 1);
        return symbol(sym.CTE_STRING, val);
    }
    
    {ID}            { return symbol(sym.ID, yytext()); }
}

/* Reglas para el estado COMMENT */
<COMMENT> {
    /* Fin del comentario */
    "*/"            { yybegin(YYINITIAL); }
    
    /* Cualquier otro caracter dentro del comentario se ignora */
    [^*]            { /* Ignorar */ }
    "*"             { /* Ignorar */ }
}

/* Manejo de Errores */
/* Para cualquier otro caracter que no es reconocido */
. { 
    System.err.println("Error Léxico: Carácter no reconocido '" + yytext() + 
                       "' en línea " + (yyline + 1) + ", columna " + (yycolumn + 1));
}