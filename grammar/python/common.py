from arpeggio import RegExMatch as _

#------------------------------------------------------------------------------

ALL = ( ' whitespace '          # single whitespace character
        ' ws '                  # one or more whitespace characters
        ' wx '                  # zero or more whitespace characters
        ' newline '             # newline, optionally preceed by whitespace
        ' blank_line '          # two newlines, intervening whitespace ok
        ' SPACE COMMA BAR EQ '  # single characters
        ' L_PAREN R_PAREN '     # ditto
        ' L_BRACKET R_BRACKET ' # ditto
      ).split()

#------------------------------------------------------------------------------

def whitespace():
    """One whitespace character: tab(9), carriage return (10), space (32)"""
    return _(r'[ \t\r]', rule_name='whitespace', skipws=False )

def ws():
    """One or more whitespace characters"""
    expr = whitespace().to_match + '+'
    return _(expr, rule_name='ws', skipws=False )

def wx():
    """Zero or more whitespace characters (often '_' in PEG)"""
    expr = whitespace().to_match + '*'
    return _(expr, rule_name='ws', skipws=False )

def SPACE():            return ' '
def COMMA():            return ','
def BAR():              return '|'
def EQ():               return '='
def L_PAREN():          return '('
def R_PAREN():          return ')'
def L_BRACKET():        return '['
def R_BRACKET():        return ']'

def newline():
    """newline with preceeding whitespace characters (if any)"""
    expr = whitespace().to_match + r'*\n'
    return _(expr, rule_name='newline', skipws=False)

def blank_line():
    expr = r'(?<=\n)' + newline().to_match
    return _(expr, rule_name='blank_line', skipws=False)

#------------------------------------------------------------------------------
