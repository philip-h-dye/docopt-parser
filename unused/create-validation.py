import sys
import os

import yaml

from prettyprinter import cpprint as pp

from docopt_parser import DocOptParserPEG

import scenarios as sx

#------------------------------------------------------------------------------

def main( argv = sys.argv ):

    parser = DocOptParserPEG()
    
    def parse(usages):
        for i in range(len(usages)):
            parse_tree = parser.parse(usages[i]) # , print_raw=True)
            usages[i] = { usages[i] : parse_tree }
        return usages

    sections = { }

    sections['general'] = parse(sx.general())
    # sections['fragments'] = parse(sx.fragments())
    # sections['trailing'] = parse(sx.trailing())
    # sections['files'] = parse(sx.files())

    with open("test-cases.yml", 'w') as outf:
        print("---", file=outf)
        yaml.dump(sections, outf)

    sys.exit(0)

#------------------------------------------------------------------------------

if __name__ == "__main__":
    sys.exit(main(sys.argv))

#------------------------------------------------------------------------------
