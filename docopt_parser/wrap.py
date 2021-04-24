from dataclasses import dataclass

from arpeggio import ParseTreeNode, Terminal, NonTerminal, StrMatch

from prettyprinter import cpprint as pp

from copy import deepcopy

#------------------------------------------------------------------------------

#
# Wrapper to emulate an Arpeggio Node
#

@dataclass
class Unwrap(object):

    value : object

    position : int = 0

    def __post_init__(self):
        assert isinstance(self.value, (list, NonTerminal))
        assert len(self.value) > 0
        assert isinstance(self.value[0], ParseTreeNode)

#------------------------------------------------------------------------------

@dataclass
class FakeNode(object):

    value : object

    position : int = 0

    _please_unwrap : int = 0

    def NO__post_init__(self):
        assert isinstance(self.value, (list, NonTerminal))
        assert len(self.value) > 0
        assert isinstance(self.value[0], ParseTreeNode)

#------------------------------------------------------------------------------

class FakeNonTerminal(NonTerminal):
    def __init__(self, rule, value):
        super(FakeNonTerminal, self).__init__(rule, 0, value)

class FakeTerminal(NonTerminal):
    def __init__(self, rule, value):
        super(FakeTerminal, self).__init__(rule, 0, value)

#------------------------------------------------------------------------------

def nt_ok(value):
    return isinstance(value, list) and isinstance(value[0], ParseTreeNode)

class WrappedList(list):
    def __init__(self, *args, **kwargs):
        self._please_unwrap = kwargs['_please_unwrap']
        del kwargs['_please_unwrap']
        super().__init__(*args, **kwargs)

#------------------------------------------------------------------------------

def wrap(value):
    if isinstance(value, list):
        if isinstance(value[0], ParseTreeNode):
            return value
        value[0] = FakeNode(value[0])
        return WrappedList(value, _please_unwrap=1)
    if isinstance(value, ParseTreeNode):
        return WrappedList([ value ], _please_unwrap=2)
    return WrappedList([ FakeNode(value) ], _please_unwrap=3)

#------------------------------------------------------------------------------

def unwrap(wrapped):
    # wrapped must be a WrappedList
    if not isinstance(wrapped, WrappedList):
        return wrapped
    if wrapped._please_unwrap == 1:
        # print('\n: unwrap 1')
        wrapped[0] = wrapped[0].value
        # pp(wrapped)
        return list(wrapped)
    if wrapped._please_unwrap == 2:
        # print(': unwrap 2')
        return wrapped[0]
    if wrapped._please_unwrap == 3:
        # print(': unwrap 3')
        return wrapped[0].value
    raise ValueError(f"unwrap_value(): unrecognized _please_unwrap value "
                     f"{wrapped._please_unwrap}")

#------------------------------------------------------------------------------

# returns how many elements added to dst
def unwrap_into(dst, idx):

    wrapped = dst[idx]

    # wrapped must be a WrappedList
    if not isinstance(wrapped, WrappedList):
        return 0

    if wrapped._please_unwrap == 1:
        wrapped[0] = wrapped[0].value
        dst[idx] = list(wrapped)
        return 0

    if wrapped._please_unwrap == 2:
        del dst[idx]
        for elt in wrapped[::-1]:
            dst.insert(idx, elt)
        return len(wrapped) - 1

    if wrapped._please_unwrap == 3:
        dst[idx] = wrapped[0].value
        return 0

    raise ValueError(f"unwrap(): unrecognized _please_unwrap value "
                     f"{wrapped._please_unwrap}")

#------------------------------------------------------------------------------

if __name__ == "__main__":

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

    n = unwrap_into(dst,1)

    # print(f": sav") ; pp(sav) ; print('')
    # print(f": dst : n = {n}") ; pp(dst) ; print('')
    # print(f": aaa") ; pp(aaa) ; print('')

    assert dst == aaa

    #--------------------------------------------------------------------------

    # Case 2 : not a list, value is a ParseTreeNode

    aaa = [ t1, n2, t1 ]
    sav = deepcopy(aaa) ; sav[1] = wrap(deepcopy(sav[1]))
    dst = deepcopy(sav)

    n = unwrap_into(dst,1)

    # print(f": sav") ; pp(sav) ; print('')
    # print(f": dst : n = {n}") ; pp(dst) ; print('')
    # print(f": aaa") ; pp(aaa) ; print('')

    assert dst == aaa

    #--------------------------------------------------------------------------

    # Case 3 : not a list, value is not a ParseTreeNode

    aaa = [ t1, s1 , t1 ]
    sav = deepcopy(aaa) ; sav[1] = wrap(deepcopy(sav[1]))
    dst = deepcopy(sav)

    n = unwrap_into(dst,1)

    # print(f": sav") ; pp(sav) ; print('')
    # print(f": dst : n = {n}") ; pp(dst) ; print('')
    # print(f": aaa") ; pp(aaa) ; print('')

    assert dst == aaa

#------------------------------------------------------------------------------
