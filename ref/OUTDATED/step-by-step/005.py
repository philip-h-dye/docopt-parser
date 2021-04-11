#!/usr/bin/env python3

# Usage:
#   my_program command --option <argument>
#   my_program [<optional-argument>]
#   my_program --another-option=<with-argument>
#   my_program (--either-that-option | <or-this-argument>)
#   my_program <repeating-argument> <repeating-argument>...
          
GRAMMAR = '''
    @@grammar::DOCOPT

    start = /[Uu][Ss][Aa][Gg][Ee][:]/ { usage_statment }+ $ ;

    usage_statment = program:program usage_expression:expression [ /\n/ ] ;

    program = /\w+/ ;

    expression
        =
        | expression term
        | expression term
        | term
        ;

    term
        =
        | term factor
        | term factor
        | factor
        ;

    factor
        =
        | '[' expression ']'
        | '(' expression ')'
        | atom
        ;

    atom
        = 
        # | atom_expr_opt_outer:/\[/ atom_expr_opt_inner:expression /]/
        # | atom_expr_grp_outer:/\(/ atom_expr_grp_inner:expression /\)/
        | atom_option_long:option_long
        | atom_option_short:option_short
        | atom_argument:argument
        | atom_command:command
        ;

    option_short
        = opt_short_stacked:/-[a-zA-Z]{2,}/
        | opt_short_w_arg:/-[a-zA-Z]/ [/\s/] opt_short_arg:argument
        | opt_short:/-[a-zA-Z]/
        ;

    option_long
        =
        | opt_long_w_arg:/--[a-zA-Z]+/ ('='|/\s/) opt_long_arg:argument
        | opt_short:/--[a-zA-Z]+/
        ;

    argument
        = /[A-Z]+/
        | /<\w+>/
        ;

    command = command:/\w+/ ;

'''
foo = """
    option
        = option_short
        | option_long
        ;

    # USAGE-STMT ::= EXPR/SEQ/(PNAME ...)
    # program option_sequence argument_sequence ;

    # usage_statment = program:program usage_opt_seq:[ option_sequence ] usage_arg_seq:[ argument_sequence ] ;
    # usage_statment = program:program usage:expression ;
    # usage_statment = program:program usage_sequence:sequence [ /\n/ ] ;

    # option_sequence = { option }* ;
    # argument_sequence = argument_sequence:{ argument }* ;

#   sequence
        # =
        # |  atom
        # |  atom sequence
        # |  atom /[.]{3}/
        # |  atom /[.]{3}/ sequence
        # ;

        | opt_short_stacked:/-[a-zA-Z]{2,}/

        # identifier = /\w[\w\d_]*/ ;
"""

#------------------------------------------------------------------------------

import sys
import json
from tatsu import parse
from tatsu.util import asjson

_indent = 4

#------------------------------------------------------------------------------

def single_ARG():
    ast = parse(GRAMMAR, 'Usage: hello FILE')
    print(json.dumps(asjson(ast), indent=_indent))
    
def single_argx():
    ast = parse(GRAMMAR, 'Usage: hello -abc --why <file>')
    print(json.dumps(asjson(ast), indent=_indent))

def several_arguments():
    ast = parse(GRAMMAR, 'Usage: hello FILE PLAN NAME <name> <file> <task>')
    print(json.dumps(asjson(ast), indent=_indent))

def my_program():
    """Usage:
         my_program command --option <argument>
         my_program [<optional-argument>]
         my_program --another-option=<with-argument>
         my_program (--either-that-option | <or-this-argument>)
         my_program <repeating-argument> <repeating-argument>...
    """
    ast = parse(GRAMMAR, ( "Usage: \n"
                           # "my_program commandx -a -b -c <argument> \n"
                           # "my_program commandx -abc <argument> \n"
                           #
                           # Without '=', there is not way to know whether
                           #   argument should be paired with '--long'.
                           #
                           # "my_program commandx --long <argument> \n"
                           # "my_program commandx --long=<argument> \n"
                           # "my_program commandx --long= <argument> \n"
                           #
                           #"my_program commandx --long=<argument> \n"
                           # "my_program commandx --option <argument>"
                           "my_program NORM <positional-argument> [<optional-argument>] \n"
                           # "my_program --another-option=<with-argument>"
                           # "my_program (--either-that-option | <or-this-argument>)"
                           # "my_program <repeating-argument> <repeating-argument>..."
                         ) )

    print(json.dumps(asjson(ast), indent=_indent))

#------------------------------------------------------------------------------

def main ( argv = sys.argv ) :
    if True : # try :
        # single_ARG()
        # single_argx()
        # several_arguments()
        my_program()
    if False : # except Exception as e :
        print(e.message)
        # import traceback
        # traceback.print_tb(e, limit=-1, file=None)

#------------------------------------------------------------------------------

if __name__ == '__main__':
    sys.exit ( main ( sys.argv ) )

#------------------------------------------------------------------------------
