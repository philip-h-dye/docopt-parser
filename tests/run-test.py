#!/usr/bin/env python3

"""
Usage:
  runtest --general   [options] ( <n>... | all )
  runtest --trailing  [options] ( <n>... | all )
  runtest --fragment  [options] ( <n>... | all )
  runtest --program   [options] ( <p-name>... | all )
  runtest --doc       [options] <doc-file>...
  runtest --explicit  [options] <doc-string>...

Parse one or more doc string test cases.

Categories :
  -p, --program    Saved example usage docs
  -d, --doc        Load the doc from the text file <doc>
  -g, --general    General usage examples
  -t, --trailing   Doc ends with trailing description
  -x, --fragment   Doc ends without newline
  -e, --explicit   Parse the <doc-string> command line argument

Select which parse tree passes to show :
  -0, --raw        Arpeggio parse of the grammar
  -1, --repeating  Assign repeating before simplification
  -2, --simpler-1  Simplified, corrected, yet still an Arpeggio Parse Tree
  -3, --simpler-2  Minor cleanup that could not be done in the first pass
  -4, --list       List view of the parse tree, no Parse Tree nodes [DEFAULT]

Options:
  -u, --usage      Only show the doc text, do not parse (overrides --terse)                   
  --terse          With --write, just show test name being processed.
  -q, --quiet      No output unless an error.
  -s, --show       Show the usage before parsing it
  --post           Show the usage after parsing it
  -v, --verbose    Show more processing details
  --debug          Show even more processing details

File Option:
  -w, --write      Write usage doc and parse trees to validation:
                     ./validation/<category>/<test>/{doc,p0,p1,p2,list}

Positional Arguments:
  all              Run all of the usages in the category
  <n>              Scenario number(s) within the category
  <p-name>         Load doc for the example program, <p-name>
  <doc-file>       Text file with docopt style usage/help

"""

examples = """Examples:
  $ runtest --general 7
  % runtest --program exportlib
  % runtest --explicit -1 -2 "Usage: copy ( ( move | fire ) | turn )"
"""

import sys
import os
import re

from pathlib import Path

import json
import yaml

from prettyprinter import cpprint as pp

from docopt import docopt

from arpeggio import visit_parse_tree

#------------------------------------------------------------------------------

sys.path.insert(0,'.')
sys.path.insert(0,'..')
sys.path.insert(0,'t')

#------------------------------------------------------------------------------
if False:
    import sys
    print(': import paths')
    for path in sys.path :
        print(path)
    print(': - - - - -')
    print('')
    sys.stdout.flush()
#------------------------------------------------------------------------------

from docopt_parser import DocOptParserPEG
# DocOptSimplifyVisitor
from docopt_parser import DocOptSimplifyVisitor_Pass1
from docopt_parser import DocOptSimplifyVisitor_Pass2
from docopt_parser import DocOptSimplifyVisitor_Pass3
from docopt_parser import DocOptListViewVisitor
# from docopt_parser import enable_debug, apply_to_tree

# pretty printing for arpeggio ParseTreeNodes with terse names
import p

import scenarios as sx

#------------------------------------------------------------------------------

__version__ = '0.4.7'

PASSES = [ 'raw', 'repeating', 'simpler-1', 'simpler-2', 'list' ]

DEFAULT_PASS = 4 # list view

validation_pattern = 'f"validation/{args.category}/{test_id}"'

#------------------------------------------------------------------------------

slurp = lambda fname : [(f.read(), f.close()) for f in [open(fname,'r')]][0][0]

#------------------------------------------------------------------------------

def main ( argv = sys.argv ) :

    if '--debug:argv' in argv :
        argv.remove('--debug:argv')
        print(f"[argv : raw arguments]\n{argv}\n")
    
    args = docopt(__doc__,version=__version__)

    options(args)

    setattr(args, 'parser', DocOptParserPEG())

    if args['--program'] or args['--doc']:
        handle_programs(args)
    elif args['--explicit']:
        handle_explicit(args)
    else:
        handle_others(args)

    return 0

#------------------------------------------------------------------------------

def options(args):

    if args['--debug']:
        print(f"[arguments:command-line]\n{args}\n")

    if args['--debug']:
        print(f"[arguments]\n{args}\n")

    if args['--quiet']:
        args['--terse'] = False

    if args['--usage']:
        args['--terse'] = False
        args._passes = set()
    else:
        passes_to_show(args)
        if args['--terse']:
            args['--raw'] = args['--repeater'] = args['--simpler-1'] = False
            args['--simpler-2'] = args['--list'] = False
            args['--show'] = args['--post'] = False

    if args['--debug']:
        print(f"[arguments:reconciled]\n{args}\n")

#------------------------------------------------------------------------------

def passes_to_show(args):

    setattr(args, '_passes', set())

    if args['--raw']:
        args._passes.add(0)
    if args['--repeating']:
        args._passes.add(1)
    if args['--simpler-1']:
        args._passes.add(2)
    if args['--simpler-2']:
        args._passes.add(3)
    if args['--list']:
        args._passes.add(4)

    if len(args._passes) < 1:
        args._passes = set(( DEFAULT_PASS, ))
        args['--raw'] = 0 in args._passes
        args['--repeating'] = 1 in args._passes
        args['--simpler-1'] = 2 in args._passes
        args['--simpler-2'] = 3 in args._passes
        args['--list'] = 4 in args._passes

    if args['--debug']:
        print(f": pass = {args._passes}")
        for idx in passes:
            name = passes[idx]
            opt  = f"--{name}"
            text = f"pass {idx} : {name}"
            print(f"  {text:<20s}  {args[opt]}")

    if False:
        print(f"  {'pass 0 : raw':<20s}  {args['--raw']}")
        print(f"  {'pass 1 : repeating':<20s}  {args['--repeating']}")
        print(f"  {'pass 2 : simpler-1':<20s}  {args['--simpler-1']}")
        print(f"  {'pass 3 : simpler-2':<20s}  {args['--simpler-2']}")
        print(f"  {'pass 4 : list':<20s}  {args['--list']}")

#------------------------------------------------------------------------------

def handle_programs(args):

    setattr(args, 'category', 'program')

    if len(args['<doc-file>']) > 0:
        pnames = args['<doc-file>']
    elif args['<p-name>'] == ['all']:
        pnames = sx.programs()
    else:
        programs = sx.programs()
        pnames = []
        for pname in args['<p-name>']:
            try :
                pnames.append( programs[ int(pname) ] )
            except ValueError:
                pnames.append( eval(sx.pname_pattern) )

    pattern_expr = sx.pname_pattern.replace('{pname}', '(.*)')[2:][:-9]+'/'
    pattern = re.compile(pattern_expr)

    parser = DocOptParserPEG(debug=True)

    for file_path in pnames:
        # print(f"file: {file_path}")
        if not Path(file_path).exists():
            print('')
            print(f"Error:  No such file '{file_path}'")
            print('')
            # print(__doc__)
            sys.exit(1)

        m = pattern.match(file_path)

        if args['--write'] and not m :
            raise ValueError(f"Can't write validation for doc '{file_path}', "
                             f"not in '{sx.pname_pattern}\n  i.e. '{pattern_expr}'")

        program_name = m.group(1) if m else None

        # print(f" pname pattern      =  '{sx.pname_pattern}'")
        # print(f" file path          =  '{file_path}'")
        # print(f" regexp pattern     =  '{pattern_expr}'")
        # print(f" program_name       =  '{program_name}'")

        parse_usage(args, doc = slurp(file_path), test_id = program_name)

#------------------------------------------------------------------------------

def handle_explicit(args):

    setattr(args, 'category', 'explicit')

    if args['--write']:
        raise ValueError(f"Can't write validation for explicit doc strings (it needs a name)")

    for doc in args['<doc-string>']:
        parse_usage(args, doc = doc)

#------------------------------------------------------------------------------

def handle_others(args):

    if args['--general']:
        setattr(args, 'category', 'general')
        usages = sx.general()
    elif args['--trailing']:
        setattr(args, 'category', 'trailing')
        usages = sx.trailing()
    elif args['--fragment']:
        setattr(args, 'category', 'fragment')
        usages = sx.fragment()

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
        print(f"Error:  '{args.category}' only takes numeric arguments, not :  {repr(non_numeric)}")
        print('')
        # print(__doc__)
        sys.exit(1)

    for n in numeric:
        if n >= len(usages):
            print(f"error:  case number {n} too large.")
            continue
        parse_usage(args, doc = usages[n], test_id = f"{n:003d}")

#------------------------------------------------------------------------------

def parse_usage(args, doc, test_id = None):

    if args['--usage']:
        print(f"{doc}")
        return

    if args['--terse']:
        print(f"- {args.category} / {test_id}")

    if args['--write']:
        dst = Path(eval(validation_pattern))
        # print(f": destination = '{dst}'")
        os.makedirs(dst, exist_ok=True)

    if args['--show']:
        print(f"input = '{doc}'")

    if args['--write']:
        with open(dst / 'doc', 'w') as f:
            f.write(doc)

    setattr(args, 'dst', Path( eval(validation_pattern) ))
    setattr(args, 'doc', doc)
    setattr(args, 'min_pass', min(args._passes))
    setattr(args, 'max_pass', max(args._passes))

    os.makedirs ( args.dst, exist_ok=True )

    tree = perform_pass ( args, 0, args.parser.parse, doc )

    if args.max_pass < 1:
        return

    tree = perform_pass ( args, 1, DocOptSimplifyVisitor_Pass1().visit, tree )    
    tree = perform_pass ( args, 2, DocOptSimplifyVisitor_Pass2().visit, tree )
    tree = perform_pass ( args, 3, DocOptSimplifyVisitor_Pass3().visit, tree )
    tree = perform_pass ( args, 4, DocOptListViewVisitor().visit, tree )

#------------------------------------------------------------------------------

def perform_pass ( cfg, _pass, fcn, *args ):

    name = PASSES [ _pass ]

    parse_tree = fcn ( *args )

    if cfg[f'--{name}'] :
        pp(parse_tree)
        if cfg['--post']:
            print(f"\ninput = '{cfg.doc}'\n")

    if cfg['--write']:
        file_name = cfg.dst / f"p{_pass}"
        with open(file_name, 'w') as f:
            pp(parse_tree, stream=f)
        target = Path(file_name).name
        symlink = cfg.dst / name
        try :
            if symlink.exists :
                os.unlink ( symlink )
        except :
            pass
        os.symlink ( target, symlink )

    return parse_tree

#------------------------------------------------------------------------------

if __name__ == "__main__":
    sys.exit(main(sys.argv))

#------------------------------------------------------------------------------
