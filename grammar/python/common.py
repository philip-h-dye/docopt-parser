import sys

from arpeggio import EOF, Optional, ZeroOrMore, OneOrMore, OrderedChoice
from arpeggio import Sequence, And, Not, StrMatch, RegExMatch
# UnorderedGroup -- all, but in any order

from prettyprinter import cpprint as pp

# from p import pp_str

#------------------------------------------------------------------------------

ALL = ( ' ws '			# captures each whitespace character
        ' wx '			# <<< Multiple whitespace or maybe lead
        ' whitespace '		# single whitespace character
        ' SPACE COMMA BAR EQ '
        ' L_PAREN R_PAREN '
        ' L_BRACKET R_BRACKET '
        ' newline '
      ).split()

#------------------------------------------------------------------------------

def whitespace():
    """One whitespace character: tab(9), carriage return (10), space (32)"""
    return RegExMatch(r'[ \t\r]', rule_name='whitespace', skipws=False )

def ws():
    """One or more whitespace characters"""
    expr = whitespace().to_match + '+'
    return RegExMatch(expr, rule_name='ws', skipws=False )

def wx():
    """Zero or more whitespace characters (often '_' in PEG)"""
    expr = whitespace().to_match + '*'
    return RegExMatch(expr, rule_name='ws', skipws=False )

def SPACE():		return ' '
def COMMA():		return ','
def BAR():		return '|'
def EQ():		return '='
def L_PAREN(): 		return '('
def R_PAREN():		return ')'
def L_BRACKET(): 	return '['
def R_BRACKET():	return ']'

def newline():
    """newline with preceeding whitespace characters (if any)"""
    expr = whitespace().to_match + r'*\n'
    #
    return RegExMatch(expr, rule_name='newline', skipws=False)
    #
    # return OrderedChoice ( [ RegExMatch(expr), EOF ], rule_name='newline', skipws=False)

# Without LookBehind(), grammar must handle it as a recursion separator#
#   ** Use regular expressioon lookbehind (?<=...)text
#   ** Keep in mind that 'look-behind requires fixed-width pattern'
#
def blank_line():
    # return Sequence( LookBehind(newline()), newline(),
    #                  rule_name='blank_line', skipws=False)
    newline_ = newline().to_match
    expr = r'(?<=\n)' + newline_
    return RegExMatch(expr, rule_name='blank_line', skipws=False)

#------------------------------------------------------------------------------
