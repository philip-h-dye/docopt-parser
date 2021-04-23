#!/usr/bin/env python3

# Usage:
#   my_program command --option <argument>
#   my_program [<optional-argument>]
#   my_program --another-option=<with-argument>
#   my_program (--either-that-option | <or-this-argument>)
#   my_program <repeating-argument> <repeating-argument>...

slurp = lambda filename : [(f.read(), f.close()) for f in [open(filename,'r')]][0][0]

GRAMMAR = slurp("docopt.peg")

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
                           # "my_program NORM <positional-argument> \n"
                           # "my_program NORM <positional-argument> [<optional-argument>] \n"
                           # "my_program --another-option=<with-argument>"
                           # "my_program (--either-that-option | <or-this-argument>)"
                           "my_program <repeating-argument> <repeating-argument>..."
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
