import sys
import os
import unicodedata
import string

from glob import iglob
from pathlib import Path

from prettyprinter import cpprint as pp, pprint as pp_plain

from arpeggio import ParseTreeNode

#------------------------------------------------------------------------------

def tprint(*args, **kwargs):
    kwargs['file'] = tprint._tty
    print(*args, **kwargs)

tprint._tty = open("/dev/tty", 'w')

#------------------------------------------------------------------------------

def print_parsed(parsed):
    if isinstance(parsed, ParseTreeNode):
        tprint(parsed.tree_str())
    else:
        pp(parsed)

#------------------------------------------------------------------------------

# https://stackoverflow.com/questions/11066400/remove-punctuation-from-unicode-formatted-strings
unicode_punctuation = \
    dict.fromkeys ( i for i in range(sys.maxunicode)
                    if unicodedata.category(chr(i)).startswith('P') )

ascii_punctuation = dict.fromkeys(string.punctuation)

punctuation = { **unicode_punctuation, **ascii_punctuation }

def remove_punctuation(text):
    return text.translate(punctuation)

if True :
    missing = [ ]
    for ch in string.punctuation :
        if ch not in punctuation :
            missing.append(ch)
    if len(missing) :
        raise ValueError(f"ASCII Punctuation ({str(type(string.punctuation))})"
                         f" missing :  {repr(missing)}")
    del missing

#------------------------------------------------------------------------------

def write_scratch ( **kwargs ) :

    scratch = write_scratch.scratch
    if not ( scratch.exists() and scratch.is_dir() ) :
        scratch.mkdir(exist_ok=True)

    color = write_scratch.color
    if not ( color.exists() and color.is_dir() ) :
        color.mkdir(exist_ok=True)

    if '_clean' in kwargs :
        if kwargs['_clean'] is True:
            for file in iglob( str( scratch / '*' ) ):
                if not Path(file).is_dir():
                    os.unlink(file)
            for file in iglob( str( color / '*' ) ):
                if not Path(file).is_dir():
                    os.unlink(file)
        del kwargs['_clean']

    for name in kwargs :
        with open ( scratch / name , 'w' ) as f :
            pp_plain( kwargs[name] , stream=f )
        with open ( color / name , 'w' ) as f :
            pp( kwargs[name] , stream=f )

write_scratch.scratch = Path('scratch')
write_scratch.color = write_scratch.scratch / 'c'

#------------------------------------------------------------------------------
