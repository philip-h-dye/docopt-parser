import unittest

from copy import deepcopy

from arpeggio import ParseTreeNode, Terminal, NonTerminal, StrMatch

from prettyprinter import cpprint as pp

#------------------------------------------------------------------------------

def is_unpackable_sequence(x):
    return isinstance(x, (list, tuple))

#------------------------------------------------------------------------------

from docopt_parser.wrap import WrappedList, FakeNode
from docopt_parser.wrap import wrap, unwrap
from docopt_parser.wrap import unwrap_at, unwrap_into, unwrap_extend

# from docopt_parser.parsetreenodes import NonTerminal_eq_strutural

#------------------------------------------------------------------------------

class Test_Case ( unittest.TestCase ):

    def setUp ( self ):
        self.dot = StrMatch('.', rule_name = 'self.dot')

        self.s1 = 's1 : string'
        self.s2 = 's2 : string'
        self.s3 = 's3 : string'

        # rule, position, value
        self.t1 = Terminal(self.dot, 0, 'one')
        self.t2 = Terminal(self.dot, 0, 'two')
        self.t3 = Terminal(self.dot, 0, 'three')

        assert not isinstance(self.t1, list)
        assert not isinstance(self.t2, list)
        assert not isinstance(self.t3, list)

        # rule, value : a list where the first element is a node
        # self.n1 = NonTerminal(self.dot, self.t1)   # TypeError: 'Terminal' object is not subscriptable
        self.n2 = NonTerminal(self.dot, [ self.t1 ])
        self.n3 = NonTerminal(self.dot, self.n2 )
        self.n4 = NonTerminal(self.dot, [ self.n2 ])

        assert isinstance(self.n2, list)
        assert isinstance(self.n3, list)
        assert isinstance(self.n4, list)

        self.v0 = self.n2
        self.v1 = [ self.s1, self.s2 ]
        self.v2 = self.t1
        self.v3s = self.s3
        self.v3t = ( self.s1, self.s2 )

    def test_000_wrap_unneccessary(self):

        w = wrap(deepcopy(self.v0))
        assert not hasattr(w, '_please_unwrap')
        assert w == self.v0

    #------------------------------------------------------------------------------

    def fcn_00x_wrap_and_unwrap(self, case, value):
        w = wrap(deepcopy(value))
        assert hasattr(w, '_please_unwrap')
        assert w._please_unwrap == case
        assert w is not value
        if False :
            pp(value)
            pp(unwrap(deepcopy(w)))
        assert unwrap(w) == value

    def test_001_wrap_and_unwrap__case_1 (self):
        # Case 1 : list but [0] is not a ParseTreeNode
        self.fcn_00x_wrap_and_unwrap(1, self.v1)

    def test_002_wrap_and_unwrap__case_2 (self):
        # Case 2 : not a list, value is a Terminal
        self.fcn_00x_wrap_and_unwrap(2, self.v2)

    def test_003_wrap_and_unwrap__case_3_string (self):
        # Case 3 : not a list, value is not a Terminal
        self.fcn_00x_wrap_and_unwrap(3, self.v3s)

    def test_004_wrap_and_unwrap__case_3_tuple (self):
        # Case 3 : not a list, value is not a Terminal
        self.fcn_00x_wrap_and_unwrap(3, self.v3t)

    #--------------------------------------------------------------------------

    def fcn_20x_unwrap_extend(self, case, value):

        debug = False

        wrapped = wrap(deepcopy(value))
        _wrapped = deepcopy(wrapped)

        assert wrapped._please_unwrap == case

        dst = [ self.t1 ]

        if debug :
            print(f": fcn_20x_unwrap_extend : case {case} : value = {value}")
            print(f"    value      = {value}")
            print(f"    wrapped    = {_wrapped}")
            print(f"    dst prior  : ") ; pp(dst)

        expect = deepcopy(dst)
        if is_unpackable_sequence(value):
            expect.extend(deepcopy(value))
        else:
            expect.append(deepcopy(value))

        result = unwrap_extend( dst, wrapped )

        if debug :
            print(f": produced :") ; pp(dst)
            print(": expected :") ; pp(expect)

        assert result == dst
        assert type(dst[1]) == type(expect[1])
        assert dst[1] == expect[1]
        assert dst == expect

    def test_201_unwrap_extend__case_1 (self):
        # Case 1 : list but [0] is not a ParseTreeNode
        self.fcn_20x_unwrap_extend(1, self.v1)

    def test_202_a_unwrap_extend__case_2_Terminal (self):
        # Case 2 : not a list, value is a Terminal
        self.fcn_20x_unwrap_extend(2, self.v2)

    def test_203_unwrap_extend__case_3__string (self):
        # Case 3 : not a list, value is not a Terminal
        self.fcn_20x_unwrap_extend(3, self.v3s)

    def test_203_unwrap_extend__case_3__tuple (self):
        # Case 3 : not a list, value is not a Terminal
        self.fcn_20x_unwrap_extend(3, self.v3t)

    #--------------------------------------------------------------------------

    def fcn_40x_unwrap_at(self, case, value):

        aaa = [ self.t1, value, self.t1 ]
        sav = deepcopy(aaa)
        sav[1] = wrap(deepcopy(sav[1]))
        assert sav[1]._please_unwrap == case
        dst = deepcopy(sav)

        expect = deepcopy(aaa)

        n = unwrap_at(dst,1)

        if False :
            print(f": produced : delta = {n}") ; pp(dst)
            print(": expected :") ; pp(expect)

        assert type(dst[1]) == type(expect[1])
        assert dst[1] == expect[1]
        assert dst == expect

    def test_401_unwrap_at__case_1 (self):
        # Case 1 : list but [0] is not a ParseTreeNode
        self.fcn_40x_unwrap_at(1, self.v1)

    def test_402_a_unwrap_at__case_2_Terminal (self):
        # Case 2 : not a list, value is a Terminal
        self.fcn_40x_unwrap_at(2, self.v2)

    def test_403_unwrap_at__case_3__string (self):
        # Case 3 : not a list, value is not a Terminal
        self.fcn_40x_unwrap_at(3, self.v3s)

    def test_403_unwrap_at__case_3__tuple (self):
        # Case 3 : not a list, value is not a Terminal
        self.fcn_40x_unwrap_at(3, self.v3t)

    #--------------------------------------------------------------------------

    def fcn_50x_unwrap_into(self, case, value):

        aaa = [ self.t1, value, self.t1 ]
        sav = deepcopy(aaa)
        sav[1] = wrap(deepcopy(sav[1]))
        assert sav[1]._please_unwrap == case
        dst = deepcopy(sav)

        expect = deepcopy(aaa)
        if is_unpackable_sequence(expect[1]):
            expect = [ expect[0], *expect[1], expect[2] ]

        n = unwrap_into(dst,1)

        if False :
            print(f": produced : delta = {n}") ; pp(dst)
            print(": expected :") ; pp(expect)

        assert type(dst[1]) == type(expect[1])
        assert dst[1] == expect[1]
        assert dst == expect

    def test_501_unwrap_into__case_1 (self):
        # Case 1 : list but [0] is not a ParseTreeNode
        self.fcn_50x_unwrap_into(1, self.v1)

    def test_502_a_unwrap_into__case_2_Terminal (self):
        # Case 2 : not a list, value is a Terminal
        self.fcn_50x_unwrap_into(2, self.v2)

    def test_503_unwrap_into__case_3__string (self):
        # Case 3 : not a list, value is not a Terminal
        self.fcn_50x_unwrap_into(3, self.v3s)

    def test_503_unwrap_into__case_3__tuple (self):
        # Case 3 : not a list, value is not a Terminal
        self.fcn_50x_unwrap_into(3, self.v3t)

#------------------------------------------------------------------------------
