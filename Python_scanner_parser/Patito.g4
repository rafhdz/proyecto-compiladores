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
//    Ejemplo en el language Patito:
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
//  Ejemplos:
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

// vars locales dentro de la función 
funcVarSection
    : VAR varDecl+
    ;

// parámetros
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
    | BOOL
    | VOID
    ;

// ======================
// 4. Bloques y statements
// ======================
block
    : LBRACE stmt* RBRACE
    ;

stmt
    : assignStmt
    | ifStmt
    | whileStmt
    | printStmt
    | funcCallStmt
    | returnStmt  
    ;

// x = expr;
assignStmt
    : ID ASSIGN expr SEMI
    ;

// Para ambos casos
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

// llamada a función como statement como: miFunc(x, y);
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
    | EQ
    ;

addExpr
    : addExpr (PLUS | MINUS) multExpr   #addOp
    | multExpr                          #toMult
    ;

multExpr
    : multExpr (TIMES | DIV | MOD) unaryExpr  #multOp
    | unaryExpr                               #toUnary
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
    | TRUE
    | FALSE
    | STRING
    | ID
    ;

returnStmt
    : RETURN LPAREN expr RPAREN SEMI
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
BOOL    : 'bool';
VOID    : 'void';
RETURN : 'return';
TRUE    : 'true';
FALSE   : 'false';

// Símbolos
ASSIGN  : '=';
PLUS    : '+';
MINUS   : '-';
TIMES   : '*';
DIV     : '/';
MOD     : '%';
GT      : '>';
LT      : '<';
NE      : '!=';
EQ      : '==';
SEMI    : ';';
COMMA   : ',';
COLON   : ':';
LPAREN  : '(';
RPAREN  : ')';
LBRACE  : '{';
RBRACE  : '}';

// Expresiones regulares
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
