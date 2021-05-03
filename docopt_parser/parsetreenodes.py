import sys

from copy import deepcopy

from arpeggio import ParseTreeNode, Terminal, NonTerminal, StrMatch

from p import pp_str

#------------------------------------------------------------------------------

def nodes_equal(a, b, verbose=False):

    if isinstance(a, NonTerminal):
        return NonTerminal_eq_structural(a, b, verbose=verbose)

    if a == b :
        return True

    if verbose :
        print(f"eq issue:  '{self.name}' vs '{other.name}' : "
              f"terminal children differ : "
              f"{pp_str(self[idx])} vs {pp_str(other[idx])}")

    return False

#------------------------------------------------------------------------------

# NonTerminal does not implement '__eq__'
#   this implementation considers content but not position

def NonTerminal_eq_structural(self, other, verbose=False):
    if False :
        from prettyprinter import cpprint as pp
        import p
        print(f": NonTerminal_eq :")
        print(f": self :")
        pp(self)
        print(f": other :")
        pp(other)

    if not isinstance(other, NonTerminal):
        if verbose :
            print(f"eq issue:  '{self.name}' vs '{other.name}' : "
                  f"Wrong type, other is {str(type(other))}")
        return False

    if self.rule_name != other.rule_name:
        if verbose :
            print(f"eq issue:  '{self.name}' vs '{other.name}' : rules differ : "
                  f"{self.rule_name} != {other.rule_name}")
        return False

    if len(self) != len(other):
        if verbose :
            print(f"eq issue:  '{self.name}' vs '{other.name}' : lengths differ : "
                  f"{len(self)} vs {len(other)}")
        return False

    for idx in range(len(self)):
        if isinstance(self[idx], NonTerminal):
            if not NonTerminal_eq_structural(self[idx], other[idx], verbose=verbose) :
                return False
        elif self[idx] != other[idx]:
            if verbose :
                print(f"eq issue:  '{self.name}' vs '{other.name}' : "
                      f"terminal children differ : "
                      f"{pp_str(self[idx])} vs {pp_str(other[idx])}")
            return False

    return True

#------------------------------------------------------------------------------

def NonTerminal_ne_structural(self, other, verbose=False):
    return not NonTerminal_eq_structural(self, other, verbose=verbose)

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

# NonTerminal_enable_structural_eq()

#------------------------------------------------------------------------------
