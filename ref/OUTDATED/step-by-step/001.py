#!/usr/bin/env python3

GRAMMAR = '''
    @@grammar::CALC


    start = expression $ ;


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


    number = /\d+/ ;
'''


if __name__ == '__main__':
    import json
    from tatsu import parse
    from tatsu.util import asjson

    ast = parse(GRAMMAR, '3 + 5 * ( 10 - 20 )')
    print(json.dumps(asjson(ast), indent=2))
