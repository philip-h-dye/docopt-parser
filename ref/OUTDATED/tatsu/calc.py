@@grammar::CALC

start
    =
    expression $
    ;

expression
    =
    | expression '+' term
    | expression '-' term
    | term
    ;

term
    =
    | term '*' factor
    | term '/' factor
    | factor
    ;

factor
    =
    | '(' expression ')'
    | number
    ;

number
    =
    /\d+/
    ;
