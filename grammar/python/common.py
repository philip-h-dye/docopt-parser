import sys

from arpeggio import RegExMatch as _

#------------------------------------------------------------------------------

ALL = ( # single character constants and rules are added dynamically
        #
        # rules
        ' whitespace '          # single whitespace character
        ' ws '                  # one or more whitespace characters
        ' wx '                  # zero or more whitespace characters
        ' newline '             # newline, optionally preceed by whitespace
        ' blank_line '          # two newlines, intervening whitespace ok
      ).split()

#------------------------------------------------------------------------------

CHARACTER_NAME_TO_CHAR = {
    'tab'               : '\t' , #   9  0x09
    'lf'                : '\n' , #  10  0x0a
    'cr'                : '\r' , #  13  0x0d
    'space'             : ' '  , #  32  0x20
    'l_paren'           : '('  , #  40  0x28
    'r_paren'           : ')'  , #  41  0x29
    'comma'             : ','  , #  44  0x2c
    'eq'                : '='  , #  61  0x32
    'l_bracket'         : '['  , #  91  0x5b
    'r_bracket'         : ']'  , #  94  0x5d
    'bar'               : '|'  , # 124  0x7c
}

#------------------------------------------------------------------------------

CHARACTER_CHAR_TO_NAME = { }

def create_character_rule(ch):
    def the_method():
        nonlocal ch
        return ch
    return the_method

module = sys.modules[__name__]
for name, ch in CHARACTER_NAME_TO_CHAR.items():
    CHARACTER_CHAR_TO_NAME[ch] = name
    setattr ( module, name.upper(), ch )
    setattr ( module, name, create_character_rule(ch) )
    ALL.append(name)
    ALL.append(name.upper)

#------------------------------------------------------------------------------

WHITESPACE_CHARS = ( TAB , CR , SPACE )
WHITESPACE_RULES = ( tab , cr , space )
WHITESPACE_NAMES = { ch : CHARACTER_CHAR_TO_NAME[ch] for ch in WHITESPACE_CHARS }

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
