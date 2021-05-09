import sys

from keyword import iskeyword

from dataclasses import dataclass

from arpeggio import ParsingExpression, EOF, RegExMatch as _ , StrMatch
from arpeggio import ParseTreeNode, Terminal

#------------------------------------------------------------------------------

ALL = ( # single character constants and rules are added dynamically
        #
        # rules
        ' whitespace '          # single whitespace character
        ' newline '             # newline, optionally preceed by whitespace
        ' blank_line '          # two newlines, intervening whitespace ok
        ' ws t_ws p_ws'         # one or more whitespace characters
        ' wx t_ws p_ws'         # zero or more whitespace characters
        ' valid_wx t_wx_newline p_wx_newline '
        ' valid_ws t_ws_newline p_ws_newline '
      ).split()

#------------------------------------------------------------------------------

@dataclass
class character (object):
    name        : str           # Must be n all uppercase valid identifier
    raw         : str           # i.e. r'\n' is two characters, not one
    alias       : str           = None
    ch          : str           = None
    name_lc     : str           = None
    rule        : object        = None
    rule_m      : object        = None

#------------------------------------------------------------------------------

# https://donsnotes.com/tech/charsets/ascii.html

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

@dataclass
class ParseSpec (object):
    text        : str
    rule        : ParsingExpression
    expect      : ParseTreeNode

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

	p_{c.name_lc} = ParseSpec( {c.name}, {c.name_lc}_m, t_{c.name_lc} )
	ALL.append(p_{c.name_lc})
"""
    exec(code.replace('\t',''), globals())

    if c.alias is not None and len(c.alias) > 0:
        c.alias_lc = c.alias.lower()
        code = f"""
	{c.alias_lc} = {c.name_lc}
	ALL.append({c.alias_lc})
	{c.alias_lc}_m = {c.name_lc}_m
	ALL.append({c.alias_lc}_m)
	t_{c.alias_lc} = t_{c.name_lc}
	ALL.append(t_{c.alias_lc})
	p_{c.alias_lc} = p_{c.name_lc}
	ALL.append(p_{c.alias_lc})
"""
    exec(code.replace('\t',''), globals())

#------------------------------------------------------------------------------

def validate_name(which, name, raw):

    p = "PACKAGE CONFIGURATION ERROR, "

    assert not iskeyword(name), \
        ( f"{p}Invalid character {which} '{name}' for '{raw}', {which} "
          f"may not be a Python keyword." )

    assert name.isidentifier(), \
        ( f"{p}Invalid character {which} '{name}' for '{raw}', {which} "
          f"is not a valid Python identifier." )

    assert name == name.upper(), \
        ( f"{p}Character {which} '{name}' is not all uppercase.  Character "
          f"name and alias constants must be all uppercase.  Lowercase "
          f"reserved for their corresponding grammar rules.")

    assert name not in CHARACTER_NAME_TO_CHAR, \
        ( f"{p}Character {which} '{name}' for '{raw}', already exists.  Prior "
          f"occurance for '{CHARACTER_NAME_TO_CHAR[name]}'")

#------------------------------------------------------------------------------

module = sys.modules[__name__]

CHARACTER_CHAR_TO_NAME = { }
CHARACTER_CHAR_TO_ALIAS = { }
CHARACTER_NAME_TO_CHAR = { }
CHARACTER_CHAR_TO_RAW = { }
CHARACTER_RAW_TO_CHAR = { }

# Arrays in order of occurance in CHARACTER_TABLE, no extra elements for aliases.
CHARACTER_CHARS = [ ]
CHARACTER_RAW = [ ]
CHARACTER_RULES = [ ]
CHARACTER_MRULES = [ ]
CHARACTER_TERMINALS = [ ]

for c in CHARACTER_TABLE :
    validate_name('name', c.name, c.raw)
    c.ch = eval(f"'{c.raw}'")
    CHARACTER_CHARS.append(c.ch)
    CHARACTER_RAW.append(c.raw)
    CHARACTER_CHAR_TO_NAME[c.ch] = c.name
    CHARACTER_NAME_TO_CHAR[c.name] = c.ch
    CHARACTER_RAW_TO_CHAR[c.raw] = c.ch
    CHARACTER_CHAR_TO_RAW[c.ch] = c.raw
    setattr ( module, c.name, c.ch )
    ALL.append(c.name)
    if c.alias is not None :
        validate_name('alias', c.alias, c.raw)
        CHARACTER_NAME_TO_CHAR[c.alias] = c.ch
        CHARACTER_CHAR_TO_ALIAS[c.ch] = c.alias
        setattr ( module, c.alias, c.ch )
        ALL.append(c.alias)
    create_character_rules_and_terminals ( c )

del module

#------------------------------------------------------------------------------

# WHITESPACE_CHARS = ( TAB , CR , SPACE )
WHITESPACE_CHARS = TAB + CR + SPACE
WHITESPACE_RAW   = tuple( [ CHARACTER_CHAR_TO_RAW[ch] for ch in WHITESPACE_CHARS ] )
WHITESPACE_RAW_STR = ''.join(WHITESPACE_RAW)
WHITESPACE_RULES = ( tab , cr , space )
WHITESPACE_NAMES = { ch : CHARACTER_CHAR_TO_NAME[ch] for ch in WHITESPACE_CHARS }

# WHITESPACE_REGEX = r'[\t\r ]'
WHITESPACE_REGEX = f"[{WHITESPACE_RAW_STR}]"
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
p_newline = ParseSpec ( LINEFEED, newline, t_newline )

t_eof = Terminal(EOF(), 0, '')
p_eof = ParseSpec ( '', EOF, t_eof )

#------------------------------------------------------------------------------

def linefeed_eol_only ( text ) :

    n_linefeeds = text.count(LINEFEED)
    # print(f"\n: n_linefeeds = {n_linefeeds}")

    if n_linefeeds <= 0 :
        raise ValueError(f"No linefeeds in <text>, one is required  "
                         "at the end.  Please address.")

    if n_linefeeds > 1 :
        raise ValueError(f"Found {n_linefeeds} linefeeds in <text>, only one "
                         "allowed, at the end.  Please address.")

    if text[-1] != LINEFEED :
        if n_linefeeds > 0 :
            raise ValueError(f"Linefeed not at end of specified <text>. "
                             "Please address." )

#------------------------------------------------------------------------------

def ensure_linefeed_eol ( text ) :

    if text is None or text == '' :
        text = LINEFEED

    if text[-1] != LINEFEED :
        text += LINEFEED

    linefeed_eol_only(text)

    return text

#------------------------------------------------------------------------------

def valid_wx ( text ) :

    for ch in text :
        if ch not in WHITESPACE_CHARS :
            raise ValueError(
                f"In specified <text> '{text}', ch '{ch}' is not a configured "
                "whitespace character ({WHITESPACE_NAMES}).  Please address." )

#------------------------------------------------------------------------------

def valid_ws ( text ) :

    missing = ( "<text> has no whitespace characters.  'ws' requires "
                "at least one.  Please address or use t_wx_newline." )

    if text is None or text == '' or text == LINEFEED :
        raise ValueError(missing)

    for ch in WHITESPACE_CHARS :
        if ch in text :
            return valid_wx(text)

    raise ValueError(missing)

#------------------------------------------------------------------------------

def t_wx_newline ( text = None ):
    """Return an arpeggio.Terminal for newline with the specified whitespace.
       If leading whitespace portion of <text> is not empty, create a newline
       Terminal with the leading whitespace followed by a linefeed.

       Simply returns t_newline if no whitespace specified.

       If ending linefeed is missing, it will be appended.

      <text> : zero or more whitespace characters, optionally followed by a
               linefeed.  May not contain more than linefeed.  If present,
               the linefeed must be last.
    """
    text = ensure_linefeed_eol(text)
    valid_wx ( text[:-1] )
    return Terminal( newline(), 0, text )

def p_wx_newline ( text ) :
    t = t_wx_newline(text)
    return ParseSpec ( t.value, newline, t )

#------------------------------------------------------------------------------

def t_ws_newline ( text ):
    """Return an arpeggio.Terminal for newline with the specified whitespace
       followed by a linefeed.  If linefeed is missing, it will be appended.

      <text> : One or more whitespace characters, optionally followed by a
               linefeed.  May not contain more than linefeed.  If present,
               the linefeed must be last.
    """
    text = ensure_linefeed_eol(text)
    valid_ws ( text[:-1] )
    return Terminal( newline(), 0, text )

def p_ws_newline ( text ) :
    t = t_ws_newline(text)
    return ParseSpec ( t.value, newline, t )

#------------------------------------------------------------------------------

def t_wx ( text ) :
    """Return an arpeggio.Terminal for wx with the specified whitespace.
       If leading whitespace portion of <text> is not empty, create a newline
       Terminal with the leading whitespace followed by a linefeed.

       Simply returns t_newline if no whitespace specified.

      <text> : zero or more whitespace characters, optionally followed by a
               linefeed.  May not contain more than linefeed.  If present,
               the linefeed must be last.
    """

    valid_wx(text)

    return Terminal( wx(), 0, text )

def p_wx ( text ) :
    return ParseSpec ( text, ws, t_ws(text) )

#------------------------------------------------------------------------------

def t_ws ( text ) :
    """Return an arpeggio.Terminal ws for the specified whitespace.
       If leading whitespace portion of <text> is not empty, create a newline
       Terminal with the leading whitespace followed by a linefeed.

       Simply returns t_newline if no whitespace specified.

      <text> : zero or more whitespace characters, optionally followed by a
               linefeed.  May not contain more than linefeed.  If present,
               the linefeed must be last.
    """

    valid_ws(text)

    return Terminal( ws(), 0, text )

def p_ws ( text ) :
    return ParseSpec ( text, ws, t_ws(text) )

#------------------------------------------------------------------------------
