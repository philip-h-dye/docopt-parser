import sys

from copy import deepcopy

from arpeggio import ParseTreeNode, Terminal, NonTerminal, StrMatch

#------------------------------------------------------------------------------

# NonTerminal does not implement '__eq__'
#   this implementation considers content but not position

def NonTerminal_eq_structural(self, other):
    if False :
        from prettyprinter import cpprint as pp
        import p
        print(f": NonTerminal_eq :")
        print(f": self :")
        pp(self)
        print(f": other :")
        pp(other)   
    if not isinstance(other, NonTerminal):
        return False
    if self.rule != other.rule:
        return False        
    if len(self) != len(other):
        return False
    for idx in range(len(self)):
        if self[idx] != other[idx]:
            return False
    return True

#------------------------------------------------------------------------------

def NonTerminal_ne_structural(self, other):
    return not NonTerminal_eq_structural(self, other)

#------------------------------------------------------------------------------

NonTerminal_eq_original = NonTerminal.__eq__
NonTerminal_ne_original = NonTerminal.__ne__

#------------------------------------------------------------------------------

def NonTerminal_enable_structural_eq():
    NonTerminal.__eq__ = NonTerminal_eq_structural
    NonTerminal.__ne__ = NonTerminal_ne_structural

def NonTerminal_restore_original_eq():
    NonTerminal.__eq__ = NonTerminal_eq_original
    NonTerminal.__ne__ = NonTerminal_ne_original

#------------------------------------------------------------------------------

NonTerminal_enable_structural_eq()

#------------------------------------------------------------------------------
