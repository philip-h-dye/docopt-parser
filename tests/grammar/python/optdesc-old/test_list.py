import sys
import os
import re

from contextlib import redirect_stdout

import unittest

from arpeggio import ParserPython, NonTerminal, Terminal, flatten
from arpeggio import Sequence, OrderedChoice, ZeroOrMore, OneOrMore, EOF
from arpeggio import RegExMatch as _

#------------------------------------------------------------------------------

from prettyprinter import cpprint as pp
from docopt_parser.parsetreenodes import NonTerminal_eq_structural
from p import pp_str

#------------------------------------------------------------------------------

from grammar.python.common import ws, COMMA, BAR
from grammar.python.operand import operand, \
    operand_all_caps, operand_angled

from grammar.python.optdesc.list import option_list
from grammar.python.optdesc.list import ol_first_option, ol_element
from grammar.python.optdesc.list import ol_operand_lead, ol_operand
from grammar.python.optdesc.list import ol_option_lead, ol_long, ol_short
from grammar.python.optdesc.list import _long, _short

#------------------------------------------------------------------------------

# from docopt_parser import DocOptParserPEG
# from docopt_parser import DocOptSimplifyVisitor_Pass1 as Simplify_Pass1
# from docopt_parser import DocOptSimplifyVisitor_Pass2 as Simplify_Pass2

#------------------------------------------------------------------------------

grammar_elements = [ ]

def element():
    # print("\n: grammar : body : element : grammar_elements :")
    # pp(grammar_elements)
    # print('\n')
    # To work properly, first argumnet of OrderedChoice must be a
    # list.  IF not, it implicitly becomes Sequence !
    return OrderedChoice ( grammar_elements, rule_name='element' )

def body():
    return OneOrMore ( element, rule_name='body' )

def document():
    return Sequence( body, EOF, rule_name='document' )

#------------------------------------------------------------------------------
first=ol_first_option
s=_short
l=_long
a=operand_angled
c=operand_all_caps
ol=ol_operand_lead

def _t(r, opt):
    return Terminal(r(), 0, opt)

#------------------------------------------------------------------------------

def re_compile(f):
    r = f()
    r.compile()
    return r.regex

re_short  = re_compile(_short)
re_long   = re_compile(_long)

def verify_option_type_match(rule, value): # rule in s or r , value : option string

    if rule is _short :
        if re_short.fullmatch(value):
            return
        if len(value) < 2:
            raise ValueError("Short option '{value}' is too short.  Please address.")
        if len(value) > 2:
            raise ValueError("Short option '{value}' is too large.  Please address.")
        raise ValueError("Short option '{value}' is invalid.  Probably invalid characters.")

    if rule is _long :
        if re_long.fullmatch(value):
            return
        if len(value) < 4:
            raise ValueError("Long option '{value}' is too short, it must be "
                             "at least two dashes and two letters.  "
                             "Please address.")
        raise ValueError("Long option '{value}' is invalid.  Probably invalid characters.")

    raise ValueError("verify_option_type_match() should be called only with "
                     "either _long or _short.  Please address.")

#------------------------------------------------------------------------------

class Test_Option_List ( unittest.TestCase ) :

    def setUp(self):

        global grammar_elements

        # grammar_elements = [ option_list, ws ]
        # self.parser = ParserPython(grammar, reduce_tree=True)

        # quiet, no parse trees displayed
        # self.debug = False

        # show parse tree for pass >= self.debug
        self.debug = 2

        # self.each = True
        self.show = True

        # # tprint._file =
        # self.tty = open("/dev/tty", 'w')

        # self.rstdout = redirect_stdout(self.tty)
        # self.rstdout.__enter__()

        tprint._on = self.show or self.debug is not False

    #--------------------------------------------------------------------------

    def tearDown (self):
        # self.rstdout.__exit__(None, None, None)
        # self.tty.close()
        # self.tty = None
        pass

    #--------------------------------------------------------------------------

    def term (self, lead, spec):
        # -> prefix with sep : bool
        # -> input fragment  : str
        # -> option-list term

        ( rule, value, *others ) = spec # may be more values
        t = Terminal(rule(), 0, value)

        if rule in [ s, l ]:
            ol_type = ol_short if rule == _short else ol_long
            verify_option_type_match(rule, value)
            return ( True, value, NonTerminal(ol_type(), [ lead, t ] ) )

        if rule == ol :
            (op, arg) = others
            return ( False, f"{value}{arg}",
                     NonTerminal( ol_operand(),
                                  [ t,
                                    NonTerminal(operand(),
                                                [Terminal(op(), 0, arg)])]))
        if rule in [ c, a ]:
            raise TypeError(f"Bare operand '{value}', without an ol_operand"
                            "wrapper not valid in option-description")

        if hasattr(rule, 'rule_name'):
            rule_name = rule.rule_name
            raise TypeError(f"Unrecognized rule, '{rule_name}', passed in "
                            f"option-list with value '{value}' -- sort it.")

        raise TypeError(f"Unrecognized rule, '{rule_name}', passed in "
                        f"option-list with value '{value}' -- sort it.")

    #--------------------------------------------------------------------------

    # FIXME:  append short spans of whitespace before and after lead
    def list_options_only ( self, first, optdef, lead=' '):
        global grammar_elements

        # input = lead.join([ val for (key, val) in optdef ])

        # print(f"\n: optdef = {repr(optdef)}\n")
        ( rule, opt ) = optdef[0]
        if not ( rule in [s, l] ):
            raise TypeError("First element of option-description is not an "
                            "option.  Please resolve")
        p_ws = Terminal(ws(), 0, ' ')
        p_first = NonTerminal(first(), [ p_ws, Terminal(rule(), 0, opt) ])
        input = ' ' + opt

        p_ol_option_lead = Terminal(ol_option_lead(), 0, lead)
        olist_ = [ ]
        for spec in optdef[1:] :
            (use_lead, input_, p_ol_term ) = self.term(p_ol_option_lead, spec)
            olist_.append ( NonTerminal(ol_element(), [p_ol_term]) )
            input += (lead if use_lead else '') + input_
        p_olist = NonTerminal(option_list(), [ p_first, olist_ ])

        p_element = NonTerminal(element(), [ p_olist ])
        p_body = NonTerminal(body(), [p_element])
        p_eof = Terminal(EOF(), 0, '')
        expect = NonTerminal(document(), [p_body, p_eof])

        grammar_elements = [ option_list, ws]
        parser = ParserPython(language_def=document ) # , reduce_tree=True)
        # pp(parser.parser_model)
        parsed = parser.parse(input)
        # tprint("\n", parsed.tree_str(), "\n")

        assert NonTerminal_eq_structural(parsed, expect), (
            f"input = '{input}' :\n"
            f"[expect]\n{pp_str(expect)}\n[parsed]\n{pp_str(parsed)}" )

    #---------------------------------------------------------------------------

    # boundry, first option handled separately from others, not a TERM
    def SKIP_test_short_single (self) :
        f=ol_first_option
        r=_short
        optdef = ( (r, '-f'), )
        self.list_options_only( f, optdef )

    #--------------------------------------------------------------------------

    # boundry, second option is 1) first TERM() of ol_list
    #                           2) first possible option-argumemt
    def SKIP_test_mixed_pair_bar(self) :
        optdef = ( (l, '--file'),
                   (ol, '=', a, '<file>'),
                 )
        self.list_options_only( first, optdef, lead=' '  )

    #--------------------------------------------------------------------------

    def SKIP_test_short_w_long_and_ws_arg__comma(self) :
        optdef = ( (s, '-f'),
                   (l, '--file'),
                   (ol, ' ', a, '<file>'),
                 )
        self.list_options_only( first, optdef, lead=', '  )

    #--------------------------------------------------------------------------

    def SKIP_test_short_w_long_and_ws_arg__three_leads_001 (self) :
        for lead in [ ' ', ', ', ' | ' ] :
            optdef = ( (s, '-f'),
                       (l, '--file'),
                       (ol, ' ', a, '<file>'),
                     )
            self.list_options_only ( first, optdef, lead=lead  )

    def SKIP_test_short_w_long_and_ws_arg__three_leads_002 (self) :
        for lead in [ ' ', ', ', ' | ' ] :
            optdef = ( (l, '--file'),
                       (s, '-f'),
                       (ol, ' ', a, '<file>'),
                     )
            self.list_options_only ( first, optdef, lead=lead  )

    def SKIP_test_short_w_long_and_ws_arg__three_leads_003 (self) :
        for lead in [ ' ', ', ', ' | ' ] :
            optdef = ( (s, '-f'),
                       (ol, ' ', a, '<file>'),
                       (l, '--file'),
                     )
            self.list_options_only ( first, optdef, lead=lead  )

    #---------------------------------------------------------------------------

    def test_rysnc_args_stress_test (self) :

        optdef = []
        def add (opt):
            if re_short.fullmatch(opt) :
                optdef.append( (s, opt) )
            elif re_long.fullmatch(opt) :
                optdef.append( (l, opt) )

        for spec in _op :
            add ( spec[0] )
            if len(spec) >= 3:
                add ( spec[1] )

        # for lead in [ ' ', ', ', ' | ' ] :
        self.list_options_only ( first, optdef, lead=', ' )

#==============================================================================

# excerpt from rsync

_op = ( ( '--verbose', '-v',            "increase verbosity" ),
        ( '--info=FLAGS',             "fine-grained informational verbosity" ),
        ( '--debug=FLAGS'            "fine-grained debug verbosity" ),
        ( '--stderr=e|a|c'           "change stderr output mode (default: errors)" ),
        ( '--quiet', '-q'              "suppress non-error messages" ),
        ( '--no-motd'                "suppress daemon-mode MOTD" ),
        ( '--checksum', '-c'           "skip based on checksum', ' not mod-time & size" ),
        ( '--archive', '-a'            "archive mode; equals -rlptgoD (no -H', '-A', '-X)" ),
        ( '--no-OPTION'              "turn off an implied OPTION (e.g. --no-D)" ),
        ( '--recursive', '-r'          "recurse into directories" ),
        ( '--relative', '-R'           "use relative path names" ),
        ( '--no-implied-dirs'        "don't send implied dirs with --relative" ),
        ( '--backup', '-b'             "make backups (see --suffix & --backup-dir)" ),
        ( '--backup-dir=DIR'         "make backups into hierarchy based in DIR" ),
        ( '--suffix=SUFFIX'          "backup suffix (default ~ w/o --backup-dir)" ),
        ( '--update', '-u'             "skip files that are newer on the receiver" ),
        ( '--inplace'                "update destination files in-place" ),
        ( '--append'                 "append data onto shorter files" ),
        ( '--append-verify'          "--append w/old data in file checksum" ),
        ( '--dirs', '-d'               "transfer directories without recursing" ),
        ( '--mkpath'                 "create the destination's path component" ),
        ( '--links', '-l'              "copy symlinks as symlinks" ),
        ( '--copy-links', '-L'         "transform symlink into referent file/dir" ),
        ( '--copy-unsafe-links'      "only 'unsafe' symlinks are transformed" ),
        ( '--safe-links'             "ignore symlinks that point outside the tree" ),
        ( '--munge-links'            "munge symlinks to make them safe & unusable" ),
        ( '--copy-dirlinks', '-k'      "transform symlink to dir into referent dir" ),
        ( '--keep-dirlinks', '-K'      "treat symlinked dir on receiver as dir" ),
        ( '--hard-links', '-H'         "preserve hard links" ),
        ( '--perms', '-p'              "preserve permissions" ),
        ( '--executability', '-E'      "preserve executability" ),
        )

#------------------------------------------------------------------------------

def tprint(*args, **kwargs):
    if tprint._on :
        kwargs['file'] = tprint._file
        print(*args, **kwargs)

tprint._file = open("/dev/tty", 'w')

tprint._on = False

#------------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()

#------------------------------------------------------------------------------
