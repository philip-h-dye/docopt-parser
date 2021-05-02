from arpeggio import RegExMatch as _

#------------------------------------------------------------------------------

ALL = ( # single characters
        ' TAB LF CR SPACE '
        ' COMMA EQ BAR '
        ' L_PAREN R_PAREN '
        ' L_BRACKET R_BRACKET '
        #
        # rules
        ' whitespace '          # single whitespace character
        ' ws '                  # one or more whitespace characters
        ' wx '                  # zero or more whitespace characters
        ' newline '             # newline, optionally preceed by whitespace
        ' blank_line '          # two newlines, intervening whitespace ok
      ).split()

#------------------------------------------------------------------------------

# name                  = char  # Dec  Hex  -- ASCII
TAB                     = '\t'  #   9  0x09
LF                      = '\n'  #  10  0x0a
CR                      = '\r'  #  13  0x0d
SPACE                   = ' '   #  32  0x20
L_PAREN                 = '('   #  40  0x28
R_PAREN                 = ')'   #  41  0x29
COMMA                   = ','   #  44  0x2c
EQ                      = '='   #  61  0x32
L_BRACKET               = '['   #  91  0x5b
R_BRACKET               = ']'   #  94  0x5d
BAR                     = '|'   # 124  0x7c

#------------------------------------------------------------------------------

def tab():              return TAB
def lf():               return LF
def cr():               return CR
def space():            return SPACE
def comma():            return COMMA
def bar():              return BAR
def eq():               return EQ
def l_paren():          return L_PAREN
def r_paren():          return R_PAREN
def l_bracket():        return L_BRACKET
def r_bracket():        return R_BRACKET

#------------------------------------------------------------------------------

WHITESPACE_CHARS = ( TAB , CR , SPACE )
WHITESPACE_CHARS = TAB + CR + SPACE
WHITESPACE_RULES = ( tab , cr , space )

WHITESPACE_REGEX = '[' + ''.join(WHITESPACE_CHARS) + ']'
def whitespace():
    """One whitespace character of tab(9), carriage return (10), space (32)"""
    return _(WHITESPACE_REGEX, rule_name='whitespace', skipws=False )

WS_REGEX = WHITESPACE_REGEX + '+'
def ws():
    """One or more whitespace characters"""
    return _(WS_REGEX, rule_name='ws', skipws=False )

WX_REGEX = WHITESPACE_REGEX + '*'
def wx():
    """Zero or more whitespace characters (often '_' in PEG)"""
    return _(WX_REGEX, rule_name='ws', skipws=False )

NEWLINE_REGEX = WX_REGEX + '\n'
def newline():
    """Newline with optional preceeding whitespace"""
    return _(NEWLINE_REGEX, rule_name='newline', skipws=False)

BLANK_LINE_REGEX = r'(?<=\n)' + NEWLINE_REGEX
def blank_line():
    """Two newlines with optional whitespace in between"""
    return _(BLANK_LINE_REGEX, rule_name='blank_line', skipws=False)

#------------------------------------------------------------------------------
