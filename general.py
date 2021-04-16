import sys
import os

import yaml

from prettyprinter import cpprint as pp

from docopt_parser import DocOptParserPEG

import scenarios as sx

#------------------------------------------------------------------------------

def main( argv = sys.argv ):

    usages = sx.general()

    parser = DocOptParserPEG()

    if len(argv) < 2:
        cases = [ 1 ]
    else:
        cases = [ int(arg) for arg in argv[1:] ]

    for n in cases:
        if n >= len(usages):
            print(f"error:  case number {n} too large.")
            continue
        usage = usages[n]
        print(f"input = '{usage}'")
        parse_tree = parser.parse(usage) # , print_raw=True)
        pp(parse_tree)

    sys.exit(0)

#------------------------------------------------------------------------------

if __name__ == "__main__":
    sys.exit(main(sys.argv))

#------------------------------------------------------------------------------
