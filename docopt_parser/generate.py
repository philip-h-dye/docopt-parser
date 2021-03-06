#!/usr/bin/env python3

"""
Usage:
  generate ( -g | -t | -x ) [options] <n>
  generate -f [options] <p-name>
  generate -d [options] <doc>

  Generate a parser for the specified grammar.

Category Options:
  -d, --doc        Load the doc from the text file <doc>.
  -f, --file       Saved example usage docs
  -g, --general    General usage examples
  -t, --trailing   Doc ends with trailing description
  -x, --fragments  Doc ends without newline

Options:
  -s, --show       Show the usage before parsing it.
  -v, --verbose    Show more processing details.
  --debug          Show even more processing details.

Positional Arguments:  
  <n>              Scenario number(s) within the category.
  <p-name>         Load doc for the example program, <p-name>.
  <doc>            Text file with docopt style usage/help.

"""
_keep = """
File Option:
  -w, --write      Write the parse tree to parse.txt,
                   parallel to the doc file (doc.txt).
  all              Run all of the usages in the category.
"""

import sys
import os

from pathlib import Path

import yaml

from prettyprinter import cpprint as pp

from docopt_parser import DocOptParserPEG

from docopt import docopt

#------------------------------------------------------------------------------

sys.path.insert(0,'.')

import scenarios as sx

#------------------------------------------------------------------------------

__version__ = '0.2.7'

#------------------------------------------------------------------------------

slurp = lambda fname : [(f.read(), f.close()) for f in [open(fname,'r')]][0][0]

#------------------------------------------------------------------------------

def main ( argv = sys.argv ) :

    args = docopt(__doc__,version=__version__)

    # print(f"{args}\n")

    if args['--general']:
        category = 'general'
        usages = sx.general()
    elif args['--trailing']:
        category = 'general'
        usages = sx.trailing()
    elif args['--fragments']:
        category = 'general'
        usages = sx.fragments()
    # elif args['--file']:
    #     usages = sx.file_usages()

    if args['--debug']:
        print(f"{args}")

    if args['--file'] or args['--doc']:
        handle_files(args)
    else:
        handle_others(args, category, usages)

#------------------------------------------------------------------------------

def handle_others(args, category, usages):

    non_numeric = []
    if args['<n>'] == ['all']:
        numeric = list(range(len(usages)))
    else:
        numeric = []
        for arg in args['<n>']:
            try :
                numeric.append( int(arg) )
            except :
                non_numeric.append(arg)

    if len(non_numeric) > 0:
        print('')
        print(f"Error:  '{category}' only takes numeric arguments, not :  {repr(non_numeric)}")
        print('')
        print(__doc__)
        sys.exit(1)

    parser = DocOptParserPEG()

    for n in numeric:
        if n >= len(usages):
            print(f"error:  case number {n} too large.")
            continue
        usage = usages[n]
        if args['--show']:
            print(f"input = '{usage}'")
        parse_tree = parser.parse(usage) # , print_raw=True)
        if args['--show']:
            pp(parse_tree)
        print('')

#------------------------------------------------------------------------------

def handle_files(args):

    if len(args['<doc>']) > 0:
        fnames = args['<doc>']
    elif args['<p-name>'] == ['all']:
        fnames = sx.files()
    else:
        fnames = []
        for fname in args['<p-name>']:
            fnames.append( eval(sx.fname_pattern) )

    parser = DocOptParserPEG()

    for file_path in fnames:
        print(f"file: {file_path}")
        if not Path(file_path).exists():
            print('')
            print(f"Error:  No such file '{file_path}'")
            print('')
            print(__doc__)
            sys.exit(1)

        usage = slurp(file_path)
        if args['--show']:
            print(f"input = '{usage}'")
        parse_tree = parser.parse(usage) # , print_raw=True)
        if args['--write'] :
            parse_path = file_path.replace('/doc.txt','/parse.txt')
            print(f"write: {parse_path}")
            with open(parse_path, 'w') as outf:
                pp(parse_tree, stream=outf)
        if args['--show']:
            pp(parse_tree)
        print('')

    sys.exit(0)

#------------------------------------------------------------------------------

if __name__ == "__main__":
    sys.exit(main(sys.argv))

#------------------------------------------------------------------------------
