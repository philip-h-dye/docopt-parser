import sys

from dataclasses import dataclass

from arpeggio import EOF, RegExMatch as _ , StrMatch, Terminal

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

@dataclass
class character (object):
    name        : str
    raw         : str
    alias       : str           = None
    ch          : str           = None
    name_lc     : str           = None
    rule        : object        = None
    rule_m      : object        = None

_c = character

CHARACTER_TABLE = [
    _c( 'TAB',          r'\t' ),
    _c( 'LF',           r'\n' , 'LINEFEED' ), #  10  0x0a
    _c( 'CR',           r'\r' , 'CARRIAGE_RETURN' ), #  13  0x0d
    _c( 'SPACE',        r' '  ), #  32  0x20
    _c( 'L_PAREN',      r'('  ), #  40  0x28
    _c( 'R_PAREN',      r')'  ), #  41  0x29
    _c( 'COMMA',        r','  ), #  44  0x2c
    _c( 'EQ',           r'='  , 'EQUALS' ), #  61  0x32
    _c( 'L_BRACKET',    r'['  ), #  91  0x5b
    _c( 'R_BRACKET',    r']'  ), #  94  0x5d
    _c( 'BAR',          r'|'  ), # 124  0x7c
]

del _c

#------------------------------------------------------------------------------

def create_character_rules_and_terminals ( c ):
    c.name_lc = c.name.lower()
    code = f"""
	def {c.name_lc} ():
	    return {c.name}
	CHARACTER_RULES.append({c.name_lc})
	ALL.append({c.name_lc})

	def {c.name_lc}_m ():
	    return StrMatch({c.name}, rule_name='{c.name_lc}')
	CHARACTER_MRULES.append({c.name_lc}_m)
	ALL.append({c.name_lc}_m)

	t_{c.name_lc} = Terminal({c.name_lc}_m(), 0, {c.name})
	CHARACTER_TERMINALS.append(t_{c.name_lc})
	ALL.append(t_{c.name_lc})    
"""
    exec(code.replace('\t',''), globals())

    if c.alias and len(c.alias) > 0:
        c.alias_lc = c.alias.lower()
        exec(f"t_{c.alias_lc} = t_{c.name_lc} \n"
             f"ALL.append(t_{c.alias_lc}) \n")

#------------------------------------------------------------------------------

module = sys.modules[__name__]

CHARACTER_CHAR_TO_NAME = { }
CHARACTER_NAME_TO_CHAR = { }
CHARACTER_CHARS = [ ]
CHARACTER_RULES = [ ]
CHARACTER_MRULES = [ ]
CHARACTER_TERMINALS = [ ]

for c in CHARACTER_TABLE :
    assert c.name == c.name.upper(), \
        ( f"Character name '{c.name}' is not all uppercase.  As constants, "
          f"character names and aliases must be all uppercase." )
    c.name_lc = c.name.lower()
    c.ch = eval(f"'{c.raw}'")
    CHARACTER_CHARS.append(c.ch)
    CHARACTER_CHAR_TO_NAME[c.ch] = c.name
    CHARACTER_NAME_TO_CHAR[c.name] = c.ch
    setattr ( module, c.name, c.ch )
    ALL.append(c.name)
    if c.alias is not None :
        assert c.alias == c.alias.upper(), \
            ( f"Character alias '{name}' is not all uppercase.  As constants, "
              f"character names and aliases must be all uppercase." )
        setattr ( module, c.alias, c.ch )
        ALL.append(c.alias)
    create_character_rules_and_terminals ( c )

del module

#------------------------------------------------------------------------------

# WHITESPACE_CHARS = ( TAB , CR , SPACE )
WHITESPACE_CHARS = TAB + CR + SPACE
WHITESPACE_RULES = ( tab , cr , space )
WHITESPACE_NAMES = { ch : CHARACTER_CHAR_TO_NAME[ch] for ch in WHITESPACE_CHARS }

# WHITESPACE_REGEX = '[' + ''.join(WHITESPACE_CHARS) + ']'
WHITESPACE_REGEX = r'[\t\r ]'
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

NEWLINE_REGEX = WX_REGEX + r'\n'
def newline():
    """Newline with optional preceeding whitespace"""
    return _(NEWLINE_REGEX, rule_name='newline', skipws=False)

BLANK_LINE_REGEX = r'(?<=\n)' + NEWLINE_REGEX
def blank_line():
    """Two newlines with optional whitespace in between"""
    return _(BLANK_LINE_REGEX, rule_name='blank_line', skipws=False)

#------------------------------------------------------------------------------

t_newline = Terminal(newline(), 0, '\n')
t_eof = Terminal(EOF(), 0, '')

#------------------------------------------------------------------------------

def t_ws_newline ( text = None ):
    """Return an arpeggio.Terminal for newline with the specified whitespace.
       If leading whitespace portion of <text> is not empty, create a newline
       Terminal with the leading whitespace followed by a linefeed.

       Simply returns t_newline if no whitespace specified.

      <text> : zero or more whitespace characters, optionally followed by a
               linefeed.  May not contain more than linefeed.  If present,
               the linefeed must be last.
    """

    if text is None or text == '' or text == LINEFEED :
        return t_newline


    n_linefeeds = text.count(LINEFEED)
    if n_linefeeds > 1 :
        raise ValueError(f"Found {n_linefeed} linefeeds in <text>, only one "
                         "allowed, at the end.  Please address.")

    if text[-1] != LINEFEED :
        if n_linefeeds > 0 :
            raise ValueError(f"Linefeed not at end of specified <text>. "
                             "Please address." )
        text = text + LINEFEED

    whitespace_ = text[:-1]

    for ch in whitespace_ :
        if ch not in WHITESPACE_CHARS :
            raise ValueError(
                f"In specified <text> '{text}', ch '{ch}' is not a configured "
                "whitespace character ({WHITESPACE_NAMES}).  Please address." )

    return Terminal( newline(), 0, text )

#------------------------------------------------------------------------------
