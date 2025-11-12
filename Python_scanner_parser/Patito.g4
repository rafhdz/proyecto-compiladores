grammar Patito;

// ======================
// 1. Regla de entrada
// ======================
program
    : PROGRAM ID SEMI
      globalVarSection?
      functionSection*
      MAIN block
      END
      EOF
    ;

// ======================
// 2. Sección de variables globales
<<<<<<< HEAD
//    Soporta:
=======
//    Ejemplo en el language Patito:
>>>>>>> 4353e9d451b2578c13b1923876e7aeabfcb60379
//    var
//        a, b, c : int;
//        x : float;
// ======================
globalVarSection
    : VAR varDecl+
    ;

varDecl
    : idList COLON type SEMI
    ;

idList
    : ID (COMMA ID)*
    ;

// ======================
// 3. Funciones
<<<<<<< HEAD
// Se debe aceptar:
=======
//  Ejemplos:
>>>>>>> 4353e9d451b2578c13b1923876e7aeabfcb60379
//  - int func(a:int, b:float) var x:int; { ... };
//  - void funcsincuerpo();
//  - void funccuerpovacio() { };
// ======================
functionSection
    : funcDecl
    ;

funcDecl
    : type ID LPAREN paramList? RPAREN
      funcVarSection?
      block?
      SEMI
    ;

<<<<<<< HEAD
// vars locales dentro de la función (misma sintaxis que globales)
=======
// vars locales dentro de la función 
>>>>>>> 4353e9d451b2578c13b1923876e7aeabfcb60379
funcVarSection
    : VAR varDecl+
    ;

<<<<<<< HEAD
// e.g. parámetros: a:int, b:float
=======
// parámetros
>>>>>>> 4353e9d451b2578c13b1923876e7aeabfcb60379
paramList
    : param (COMMA param)*
    ;

param
    : ID COLON type
    ;

// tipos
type
    : INT
    | FLOAT
    | VOID
    ;

// ======================
// 4. Bloques y statements
// ======================
block
    : LBRACE stmt* RBRACE
    ;

<<<<<<< HEAD
// cada stmt en tus tests termina con ';'
=======
>>>>>>> 4353e9d451b2578c13b1923876e7aeabfcb60379
stmt
    : assignStmt
    | ifStmt
    | whileStmt
    | printStmt
    | funcCallStmt
    ;

// x = expr;
assignStmt
    : ID ASSIGN expr SEMI
    ;

<<<<<<< HEAD
=======
// Para ambos casos
>>>>>>> 4353e9d451b2578c13b1923876e7aeabfcb60379
// if (cond) { ... };
// if (cond) { ... } else { ... };
ifStmt
    : IF LPAREN expr RPAREN block (ELSE block)? SEMI
    ;

// while (cond) do { ... };
whileStmt
    : WHILE LPAREN expr RPAREN DO block SEMI
    ;

// print("texto", x, y+1);
printStmt
    : PRINT LPAREN printArgList? RPAREN SEMI
    ;

printArgList
    : expr (COMMA expr)*
    ;

<<<<<<< HEAD
// llamada a función como statement: miFunc(x, y);
=======
// llamada a función como statement como: miFunc(x, y);
>>>>>>> 4353e9d451b2578c13b1923876e7aeabfcb60379
funcCallStmt
    : funcCall SEMI
    ;

// llamada a función en expresión
funcCall
    : ID LPAREN argList? RPAREN
    ;

argList
    : expr (COMMA expr)*
    ;

// ======================
// 5. Expresiones
//  - aritmética: + - * /
//  - relacionales: > < !=
//  - paréntesis
//  - unarios: +x, -x
// ======================

expr
    : expr relop expr        #relExpr
    | addExpr                #toAdd
    ;

relop
    : GT
    | LT
    | NE
    ;

addExpr
    : addExpr (PLUS | MINUS) multExpr   #addOp
    | multExpr                          #toMult
    ;

multExpr
    : multExpr (TIMES | DIV) unaryExpr  #multOp
    | unaryExpr                         #toUnary
    ;

unaryExpr
    : (PLUS | MINUS) unaryExpr          #unarySign
    | atom                              #toAtom
    ;

atom
    : LPAREN expr RPAREN
    | funcCall
    | CTE_INT
    | CTE_FLOAT
    | STRING
    | ID
    ;

// ======================
// 6. LÉXICO
// ======================

// Palabras clave
PROGRAM : 'program';
VAR     : 'var';
MAIN    : 'main';
END     : 'end';
IF      : 'if';
ELSE    : 'else';
WHILE   : 'while';
DO      : 'do';
PRINT   : 'print';
INT     : 'int';
FLOAT   : 'float';
VOID    : 'void';

// Símbolos
ASSIGN  : '=';
PLUS    : '+';
MINUS   : '-';
TIMES   : '*';
DIV     : '/';
GT      : '>';
LT      : '<';
NE      : '!=';
SEMI    : ';';
COMMA   : ',';
COLON   : ':';
LPAREN  : '(';
RPAREN  : ')';
LBRACE  : '{';
RBRACE  : '}';

<<<<<<< HEAD
// Literales
=======
// Expresiones regulares
>>>>>>> 4353e9d451b2578c13b1923876e7aeabfcb60379
CTE_FLOAT
    : DIGIT+ '.' DIGIT+
    ;

CTE_INT
    : DIGIT+
    ;

STRING
    : '"' (~["\\] | '\\' .)* '"'
    ;

// Identificadores 
ID
    : [a-zA-Z_][a-zA-Z_0-9]*
    ;

// ======================
// 7. Comentarios y espacios
// ======================
LINE_COMMENT
    : '//' ~[\r\n]* -> skip
    ;

BLOCK_COMMENT
    : '/*' .*? '*/' -> skip
    ;

WS
    : [ \t\r\n]+ -> skip
    ;

// fragment
fragment DIGIT : [0-9] ;