# usage-section ->
#    r'(?i)usage :'
#    usage-pattern +                # program, option, operand and other arguments
#       program usage-expression*
#          usage-expression :
#             '[options]'           # only once
#             option [option-argument]
#             operand
#             command
#             repeating             # ...
#             choice                # a | b
#             required              # ( expr )
#             optional              # [ expr ]

from arpeggio import Sequence, OrderedChoice, ZeroOrMore, OneOrMore
from arpeggio import EOF, Optional, RegExMatch as _

from .common import *

from .option import *
from .operand import *
from .text import string_no_whitespace

def command():
    return _( string_no_whitespace().to_match,
              rule_name="command", skipws=True )

def program():
    return _( string_no_whitespace().to_match,
              rule_name="program", skipws=True )

# choice = expression ( BAR expression )*
def choice():
    return Sequence( ( expression, ZeroOrMore( ( bar, expression ) ) ),
                     rule_name="choice", skipws=True )

def expression():
    return OneOrMore ( repeatable,
                     rule_name="expression", skipws=True )

def repeatable():
    return Sequence( ( term, Optional(repeating) ),
                     rule_name="repeatable", skipws=True )

REPEATING = '...'
def repeating():
    return StrMatch ( REPEATING,
                      rule_name="repeating", skipws=True )
def term():
    # EOF causes hang in optional/required
    return OrderedChoice( [ options_shortcut, optional, required, argument ],
                     rule_name="term", skipws=True )
def optional():
    return Sequence ( ( l_bracket, choice, r_bracket, ) ,
                     rule_name="optional", skipws=True )
def required():
    return Sequence ( ( l_paren, choice, r_paren, ) ,
                     rule_name="required", skipws=True )
def argument(): 
    # EOF causes hang in optional/required
    return Sequence( ( wx, OrderedChoice( [ option, operand, command ] ) ),
                     rule_name="argument", skipws=True )

def options_shortcut():
    return _( r'(?i)\[options\]',
              rule_name="options_shortcut", skipws=True )

def usage_pattern():
    return OrderedChoice( [ options_shortcut,		# at most once
                            option,
                            operand,
                            command ],
                          rule_name="usage_pattern", skipws=True)

def usage_pattern():
    # usage_pattern = OR? program choice?
    return Sequence( Optional('OR'), program, Optional(choice) )

# usage_line = usage_pattern newline / usage_pattern EOF
def usage_line():
    return OrderedChoice( [(usage_pattern, newline), (usage_pattern, EOF)],
                          rule_name="usage_line", skipws=True )

def usage_intro():
    return Sequence( ( _(r'(?i)^\s*Usage\s*:'),
                       ZeroOrMore( OrderedChoice( [ wx, newline ] ) ) ),
                     rule_name="usage_intro", skipws=True)

def usage_section():
    return Sequence ( ( usage_intro, OneOrMore(usage_pattern) ) ,
                      rule_name="usage_section", skipws=True )
