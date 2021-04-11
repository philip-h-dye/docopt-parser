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

    # USAGE-STMT ::= EXPR/SEQ/(PNAME ...)
    # program option_sequence argument_sequence ;

    # usage_statment = program:program usage_opt_seq:[ option_sequence ] usage_arg_seq:[ argument_sequence ] ;
    # usage_statment = program:program usage:expression ;
    usage_statment = program:program usage_sequence:sequence [ /\n/ ] ;

    program = /\w+/ ;

    command = command:/\w+/ ;

    # option_sequence = { option }* ;

    # argument_sequence = argument_sequence:{ argument }* ;

    expression
        =
        |  sequence
        |  sequence /|/ expression
        ;

    sequence = { sequence_atom:atom }* ;
        # =
        # |  atom
        # |  atom sequence
        # ;
        # |  atom /[.]{3}/
        # |  atom /[.]{3}/ sequence

    atom
        = 
        | atom_option:option
        | atom_argument:argument
        | atom_command:command
        ;
        # | /\[/ expression /\]/
        # | /\(/ expression /\)/
        # | option_long
        # | option_short
     
    argument
        =
        |  /[A-Z]+/
        |  /<\w+>/
        ;

    option
        =
        | option_short
        | option_long
        ;

    option_short
        =
        | opt_short_stacked:/-[a-zA-Z]{2,}/
        | opt_short_w_arg:/-[a-zA-Z]/ [/\s/] opt_short_arg:argument
        | opt_short:/-[a-zA-Z]/
        ;

    option_long
        =
        | opt_long_w_arg:/--[a-zA-Z]+/ ('='|/\s/) opt_long_arg:argument
        | opt_short:/--[a-zA-Z]+/
        ;


'''
foo = """
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
                           "my_program commandx --long=<argument> \n"
                           # "my_program commandx --long= <argument> \n"
                           #
                           #"my_program commandx --long=<argument> \n"
                           # "my_program commandx --option <argument>"
                           # "my_program commandx --option <argument>"
                           # "my_program [<optional-argument>]")
                           # "my_program --another-option=<with-argument>"
                           # "my_program (--either-that-option | <or-this-argument>)"
                           # "my_program <repeating-argument> <repeating-argument>..."
                         ) )

    print(json.dumps(asjson(ast), indent=_indent))

#------------------------------------------------------------------------------

def main ( argv = sys.argv ) :
    try :
        # single_ARG()
        # single_argx()
        # several_arguments()
        my_program()
    except Exception as e :
        print(e.message)
        import traceback
        traceback.print_tb(e, limit=-1, file=None)

#------------------------------------------------------------------------------

if __name__ == '__main__':
    sys.exit ( main ( sys.argv ) )

#------------------------------------------------------------------------------
