import sys
import os
import unicodedata

from glob import glob
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

def remove_punctuation(text):
    return text.translate(unicode_punctuation)

#------------------------------------------------------------------------------

def write_scratch ( **kwargs ) :

    if '_clean' in kwargs :
        if kwargs['_clean'] is True:
            for file in glob("scratch/*"):
                if not Path(file).is_dir():
                    os.unlink(file)
        del kwargs['_clean']

    for name in kwargs :
        with open ( f"scratch/{name}", 'w' ) as f :
            pp_plain( kwargs[name] , stream=f )

#------------------------------------------------------------------------------
