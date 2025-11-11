grammar Patito;

program : ID EOF;
ID      : [a-zA-Z]+ ;
WS      : [ \t\r\n]+ -> skip ;