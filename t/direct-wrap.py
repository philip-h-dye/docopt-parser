from dataclasses import dataclass

from copy import deepcopy

from prettyprinter import cpprint as pp

from arpeggio import ParseTreeNode, Terminal, NonTerminal, StrMatch

from docopt_parser.parsetreenodes import *
from docopt_parser.wrap import *

#------------------------------------------------------------------------------

def is_unpackable_sequence(x):
    return isinstance(x, (list, tuple))

#------------------------------------------------------------------------------
if True :

    dot = StrMatch('.', rule_name = 'dot')

    s1 = 's1 : string'

    # rule, position, value
    t1 = Terminal(dot, 0, 'one')
    t2 = Terminal(dot, 0, 'two')
    t3 = Terminal(dot, 0, 'three')

    assert not isinstance(t1, list)
    assert not isinstance(t2, list)
    assert not isinstance(t3, list)

    # rule, value : a list where the first element is a node
    # n1 = NonTerminal(dot, t1)   # TypeError: 'Terminal' object is not subscriptable
    n2 = NonTerminal(dot, [t1])
    n3 = NonTerminal(dot, n2)
    n4 = NonTerminal(dot, [n2])

    assert isinstance(n2, list)
    assert isinstance(n3, list)
    assert isinstance(n4, list)

    v0 = n2
    v1 = [ 'v1 : string 1', 'v1 : string 2' ]
    v2 = t1
    v3 = 'v3 : string'

    w0 = wrap(deepcopy(v0))
    assert not hasattr(w0, '_please_unwrap')
    assert w0 == v0

    w1 = wrap(deepcopy(v1))
    assert hasattr(w1, '_please_unwrap')
    assert w1._please_unwrap == 1
    assert w1 is not v1
    # pp(v1)
    # pp(unwrap(deepcopy(w1)))
    assert unwrap(w1) == v1

    w2 = wrap(deepcopy(v2))
    assert hasattr(w2, '_please_unwrap')
    # print(f": w2._please_unwrap == {w2._please_unwrap}")
    assert w2._please_unwrap == 2
    assert w2 is not v2
    # pp(v2)
    # pp(unwrap(deepcopy(w2)))
    # pp(w2)
    assert unwrap(w2) == v2

    w3 = wrap(deepcopy(v3))
    assert hasattr(w3, '_please_unwrap')
    # print(f": w3._please_unwrap == {w3._please_unwrap}")
    assert w3._please_unwrap == 3
    assert w3 is not v3
    # pp(v3)
    # pp(unwrap(deepcopy(w3)))
    assert unwrap(w3) == v3

    #--------------------------------------------------------------------------

    # Case 1 : list but [0] is not a ParseTreeNode

    aaa = [ t1, v1, t2 ]
    sav = deepcopy(aaa) ; sav[1] = wrap(deepcopy(sav[1]))
    dst = deepcopy(sav)

    expect = [ t1, *v1, t2 ]

    n = unwrap_into(dst,1)

    if False :
        # print(f": aaa") ; pp(aaa) ; print('')
        # print(f": sav") ; pp(sav) ; print('')
        print(f": dst : n = {n}") ; pp(dst) ; print('')
        print(f": exp") ; pp(expect) ; print('')

    assert dst == expect

    #--------------------------------------------------------------------------

    # Case 2 : not a list, value is a Terminal

    aaa = [ t1, n2, t1 ]
    sav = deepcopy(aaa) ; sav[1] = wrap(deepcopy(sav[1]))
    dst = deepcopy(sav)

    n = unwrap_into(dst,1)

    # print(f": sav") ; pp(sav) ; print('')

    if True :
        print(f": dst : n = {n}") ; pp(dst) ; print('')
        print(f": aaa") ; pp(aaa) ; print('')
        

    assert dst == aaa

    #--------------------------------------------------------------------------

    # Case 3 : not a list, value is not a Terminal

    aaa = [ t1, s1 , t1 ]
    sav = deepcopy(aaa) ; sav[1] = wrap(deepcopy(sav[1]))
    dst = deepcopy(sav)

    n = unwrap_into(dst,1)

    if True :
        # print(f": sav") ; pp(sav) ; print('')
        print(f": dst : n = {n}") ; pp(dst) ; print('')
        print(f": aaa") ; pp(aaa) ; print('')
        pass

    assert dst == aaa

#------------------------------------------------------------------------------
