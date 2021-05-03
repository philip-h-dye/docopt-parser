import sys

from arpeggio import RegExMatch as _ , StrMatch

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
    'TAB'               : '\t' , #   9  0x09
    'LF'                : '\n' , #  10  0x0a
    'CR'                : '\r' , #  13  0x0d
    'SPACE'             : ' '  , #  32  0x20
    'L_PAREN'           : '('  , #  40  0x28
    'R_PAREN'           : ')'  , #  41  0x29
    'COMMA'             : ','  , #  44  0x2c
    'EQ'                : '='  , #  61  0x32
    'L_BRACKET'         : '['  , #  91  0x5b
    'R_BRACKET'         : ']'  , #  94  0x5d
    'BAR'               : '|'  , # 124  0x7c
}

#------------------------------------------------------------------------------

def create_character_rule(method_name, ch_name):
    code = f"""
def {method_name} ():
    return StrMatch({ch_name}, rule_name='{method_name}')
"""
    exec(code, globals())

    return eval(method_name)

#------------------------------------------------------------------------------

module = sys.modules[__name__]

CHARACTER_CHAR_TO_NAME = { }
CHARACTER_CHARS = [ ]
CHARACTER_RULES = [ ]

for name, ch in CHARACTER_NAME_TO_CHAR.items():
    assert name == name.upper(), \
        "As constants, character names should be uppercase."
    CHARACTER_CHAR_TO_NAME[ch] = name
    method_name = name.lower()
    setattr ( module, name, ch )
    rule = create_character_rule ( method_name, name )
    CHARACTER_CHARS.append(ch)
    CHARACTER_RULES.append(rule)
    ALL.append(name)
    ALL.append(method_name)

del module
del name
del ch
del rule

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
    return _(WX_REGEX, rule_name='wx', skipws=False )

NEWLINE_REGEX = WX_REGEX + '\n'
def newline():
    """Newline with optional preceeding whitespace"""
    return _(NEWLINE_REGEX, rule_name='newline', skipws=False)

BLANK_LINE_REGEX = r'(?<=\n)' + NEWLINE_REGEX
def blank_line():
    """Two newlines with optional whitespace in between"""
    return _(BLANK_LINE_REGEX, rule_name='blank_line', skipws=False)

#------------------------------------------------------------------------------
