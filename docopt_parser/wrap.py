from dataclasses import dataclass

from copy import deepcopy

from prettyprinter import cpprint as pp

from arpeggio import ParseTreeNode, Terminal, NonTerminal, StrMatch

from .parsetreenodes import *

#------------------------------------------------------------------------------

def is_unpackable_sequence(x):
    return isinstance(x, (list, tuple))

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

from contextlib import redirect_stdout

_tty = None

def tprint(*args, **kwargs):
    global _tty
    if False :
        if _tty is None :
            _tty = open("/dev/tty", "w")
        with redirect_stdout(_tty) :
            print(*args, **kwargs)         

#------------------------------------------------------------------------------

def wrap(value):
    """Wrap <value> such that NonTerminal will accept it as a list of Parse Tree Nodes.
       Does nothing if <value> is already capable of being such.
"""
    tprint(f": wrap : value = {value}")

    # Note: NonTerminal value is Case 0 since NonTerminal is a sub-type of list
    #         and a NonTerminal [0] is always a ParseTreeNode

    if isinstance(value, list):

        if isinstance(value[0], ParseTreeNode):
            # Case 0 : not wrapped : list and [0] is a ParseTreeNode
            tprint(f"  => not wrapped : Case 0 : list and [0] is a ParseTreeNode")
            return value

        # Case 1 : list but [0] is not a ParseTreeNode
        tprint(f"  => wrapped : Case 1 : list but [0] is not a ParseTreeNode")
        value[0] = FakeNode(value[0])
        return WrappedList(value, _please_unwrap=1)
    
    if isinstance(value, Terminal):
        # Case 2 : not a list, value is a Terminal
        tprint(f"  => wrapped : Case 2 : not a list, value is a Terminal")
        return WrappedList([ value ], _please_unwrap=2)

    # Case 3 : not a list, value is not a Terminal
    tprint(f"  => wrapped : Case 3 : not a list, value is not a Terminal")
    return WrappedList([ FakeNode(value) ], _please_unwrap=3)

#------------------------------------------------------------------------------

def unwrap(wrapped):
    """ ...
    """
    # wrapped must be a WrappedList
    if not isinstance(wrapped, WrappedList):
        return wrapped
    # Case 1 : list but [0] is not a ParseTreeNode
    if wrapped._please_unwrap == 1:
        # print('\n: unwrap 1')
        wrapped[0] = wrapped[0].value
        # pp(wrapped)
        return list(wrapped)
    # Case 2 : not a list, value is a Terminal
    if wrapped._please_unwrap == 2:
        # print(': unwrap 2')
        return wrapped[0]
    # Case 3 : not a list, value is not a Terminal
    if wrapped._please_unwrap == 3:
        # print(': unwrap 3')
        return wrapped[0].value
    raise ValueError(f"unwrap_value(): unrecognized _please_unwrap value "
                     f"{wrapped._please_unwrap}")

#------------------------------------------------------------------------------

def unwrap_extend(dst, wrapped):

    """appends unwrapped element(s) to the end list 'dst'"""

    debug = False

    if debug:
        print(f"\n[ unwrap_extend : enter")
        print("[wrapped]")
        pp(wrapped)
    
    value = unwrap(wrapped)

    if debug:
        print("[value]")
        pp(value)

    if debug:
        print("[dst] : before")
        pp(dst)

    if is_unpackable_sequence(value):
        dst.extend(value)
    else:
        dst.append(value)

    if debug:
        print("[dst] : after")
        pp(dst)

    return dst

#------------------------------------------------------------------------------

def unwrap_at(dst, idx):
    dst[idx] = unwrap(dst[idx])
    return dst[idx]
    
#------------------------------------------------------------------------------

# returns how many elements added to dst
def unwrap_into(dst, idx):

    """Replaces wrapped element dst[idx] with unwrapped value.
       if unwrapped value is a list or NonTerminal, explode list in place.
       return number additional elements added to the list.
       (i.e. zero (0) when values isn't a list or NonTerminal)
    """

    wrapped = dst[idx]

    tprint(f": unwrap_into : type(wrapped?) = {str(type(wrapped))}")
    
    # wrapped is always a WrappedList
    if not isinstance(wrapped, WrappedList):
        tprint(f"  => not a WrappedList  -- nothing to do")
        return 0

    value = unwrap(wrapped)

    tprint(f": unwrap_into : type(value) = {str(type(value))}")

    if not is_unpackable_sequence(value):
        tprint(f"  => not an unpackable sequence, simply assign value to dst[idx]")
        dst[idx] = value
        return 0
        
    tprint(f"  : exploding inplace")

    del dst[idx]

    for elt in value[::-1]:
        dst.insert(idx, elt)

    delta = len(value) - 1
    tprint(f"  => delta = {delta}")
    return delta

#------------------------------------------------------------------------------
