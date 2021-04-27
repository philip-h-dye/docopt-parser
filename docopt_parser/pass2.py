
import sys
import os
import io
import re

from contextlib import redirect_stdout

from dataclasses import dataclass

from prettyprinter import cpprint as pp

import arpeggio
import arpeggio.cleanpeg
from arpeggio import ( Terminal, NonTerminal, StrMatch, SemanticActionResults, ParseTreeNode )

from .wrap import WrappedList, wrap, unwrap, unwrap_extend

# FIXME: only while debugging
from p import pp_str

#------------------------------------------------------------------------------

def dprint(*args, **kwargs):
    if dprint.debug :
        print(*args, **kwargs)

dprint.debug = False

#------------------------------------------------------------------------------

def sprint(*args, **kwargs):
    with io.StringIO() as f:
        kwargs['file'] = f
        print(*args, **kwargs)
        return f.getvalue()

def internal_error(context, node, *args, **kwargs):
    msg = sprint(*args, **kwargs)
    out = ( f"INTERNAL ERROR : {context} : {node.name} -- {msg}\n"
            f"{pp_str(node)}"
            f"Please report this to the maintainer, <phdye@acm.org>.\n"
            f"Thank you and have a wonderful day !")

#------------------------------------------------------------------------------

class DocOptSimplifyVisitor_Pass2(object):

    classes = \
        ( ' divulge_list '
          ' divulge_single '
          ' divulge_terminal '
          ' text '
          ' empty '
        ) . split()

    UNUSED_unwrap = \
        ( ' other_sections other '
          ' required '		# explicit no differnet than explicit
          # ' expression '  	# NO, determinant for sides of implicit choice
          ' term argument '
          ' usage_line '          # NOT: usage or usage_pattern
          ' option short long long_with_eq_all_caps long_with_eq_angle '
          ' option_line option_list option_single '
          ' operand_line ' # operand_section '
          # ' short_no_arg short_stacked '	-- necessary for semantics
          # ' long_no_arg long_with_eq_arg '	-- necessary for semantics
        )

    # A 'list' being a NonTerminal with one or more children
    _divulge_list = \
        ( ' other_sections '
          ' required '
          ' term '
          # NOT why working on option.list # ' list '
          # !o # ' option_list '
          ' option_list_comma '
          ' option_list_bar '
          ' option_list_space '
        )

    # A 'single' being a NonTerminal with only one child
    _divulge_single = \
        ( ' other '
          ' usage_line '          # NOT usage or usage_pattern
          ' argument '
          # !o # ' option '
          ' short '
          ' long '
          ' option_line option_single '
          # ' long_with_eq_arg '
        )

    # A 'terminal' being, obviously, a Terminal node, contents in node.value
    _divulge_terminal = \
        ( ' short_no_arg_ '
          ' '
          # TERMINALS: short_no_arg short_stacked long_with_eq_all_caps long_with_eq_angle
        )

    _text = \
        ( ' intro '
          ' operand_help '
          ' option_help '
          ' short_no_arg '
          ' long_no_arg '
          ' operand_no_space '
          # ' operand_intro operand_help  '
          # ' option_intro option_help '
        )

    _empty = \
        ( ' intro_line '
          ' usage_entry '
          ' operand_all_caps operand_angle '
          ' EQ LPAREN RPAREN LBRACKET RBRACKET OR COMMA EOF blankline newline '
        )

    # Used to make BAR directly searchable within the choice list
    BAR = Terminal(StrMatch('|', rule_name='BAR'), 0, '|')

    # '--long= <argument>' => '--long' '=' '<argument>'
    # FIXME: revamp grammar to explicitly handle all whitespace, see issues.txt
    EQ = Terminal(StrMatch('=', rule_name='repeated'), 0, '=')

    #--------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):

        dprint.debug = False

        dprint(": pass 2 : init : ENTER")

        super().__init__(*args, **kwargs)

        # 'unwrap' -- did way too much, break into judiciously defined
        #             groupings that can be handled easily and explicitly.

        for _class in self.classes :
            dprint(f"  : handler '{_class}'")
            method = getattr(self, _class)
            for rule_name in getattr(self, f"_{_class}").split() :
                alias = f"visit_{rule_name}"
                dprint(f"     - rule '{rule_name}'")
                setattr(self, alias, method)

        dprint(": pass 2 : init : LEAVE")

    #--------------------------------------------------------------------------

    def visit(self, node, depth=0, path=[]):

        i = ' ' * 3 * depth

        dprint('')
        dprint(f"{i} : visit : {node.name} -- START")

        if not isinstance(node, (NonTerminal, Terminal, SemanticActionResults)):
            dprint(f"{i}   ** Invalid type '{str(type(node))}'")
            dprint(f"{i}   => {_res(node)}")
            dprint(f"{i} : visit : {node.name} -- DONE")
            return node

        #----------------------------------------------------------------------

        dprint('')
        dprint(f"{i}   Process Children -- START")
        dprint(f"{i}     # essentially, thus :")
        dprint(f"{i}     children = []")
        dprint(f"{i}     for child in node :")
        dprint(f"{i}         response = visit(child)")
        dprint(f"{i}         if response is not None :")
        dprint(f"{i}            children.append(response)  # generally reformed")
        dprint('')

        children = []
        if isinstance(node, (NonTerminal, SemanticActionResults)):
            # these object types are lists
            for child in node : # NonTerminal IS the list
                #print(f"{i}   Process Children -- START")
                if hasattr(child, 'name'):
                    dprint(f"{i}   - '{child.name}'")
                else:
                    if hasattr(child, '__name__'):
                        dprint(f"{i}   - '{child.__name__}'")
                    else:
                        dprint(f"{i}   - id = {id(child)} : {str(type(child))}")
                response = self.visit(child, depth=1+depth, path=path+[node.name])
                dprint(f"{i}   - '{child.name}'")
                dprint(f"{i}     : response   = {_res(response)}")
                if response is not None:
                    value = unwrap(response)
                    dprint(f"{i}     : unwrapped  = {_res(value)}")
                    children.append(value)

        dprint('')
        dprint(f"[ children : final ]\n{_res(children)}")
        dprint(f"{i}   Process Children -- Done\n")
        dprint('')

        #----------------------------------------------------------------------

        # In extreme circumstances, rule_name may be list.  Note, that
        # such probably means unwrapping has gone too far and your node
        # is merely an empty list.
        rule_name = str(node.rule_name)
        # print(f": visit : {rule_name}")
        method = f"visit_{rule_name}"
        if hasattr(self, method):
            dprint(f"\n*** VISIT_{node.name} -- START")
            out = getattr(self, method)(node, children)
            dprint(f"   => {_res(out)}\n")
            dprint("*** VISIT_{node.name} -- DONE\n")
            dprint('')
            return out

        if isinstance(node, Terminal):
            dprint(f"{i}   Terminal without a visit method.  Return unchanged.")
            dprint(f"{i}   => {_res(node)}")
            dprint(f"{i} : visit : {node.name} -- DONE")
            dprint('')
            return node

        if len(children) > 0:

            if type(children) is list and len(children) == 1 :
                if type(children[0]) is list :
                    dprint(f": visit : {node.name} : list w/ single child, divulge")
                    children = children[0]

            if isinstance(children, (list, NonTerminal)):
                which = None
                if isinstance(children[0], ParseTreeNode):
                    dprint(f": visit : {node.name} : list w/ children => NonTerminal")
                    out = NonTerminal(node.rule, children)
                    verb = 'is'
                    #
                    # *NO* : it strips rule info which we need.
                    #  was :
                    #     out = NonTerminal(node.rule, wrap(None))
                    #     del out[0]
                    #     out.extend(children)
                    #
                else :
                    out = NonTerminal(node.rule, wrap(children))
                    verb = 'is not'
                dprint('')
                dprint(f"{i}   : list or NonTerminal and [0] {verb} a node")
                dprint(f"{i}   => {_res(out)}")
                dprint(f"{i} : visit : {node.name} -- DONE")
                dprint('')
                return out

            internal_error(context, node, "Has children but neither a list nor "
                           "ParseTreeNode.  Nothing left to try.  ")

            raise ValueError(f"Visiting {node.name}, nothing left to try.")

        # - node can't be a terminal node (as they bailed earlier).
        # - node can't be the result of a visit_* method (bailed earlier).
        #
        # - Academically, we should crash.  Let's continue in Battle Mode
        #   and wrap it in a Terminal -- complaining first.        

        with redirect_stdout(sys.stderr):
            print(f"INTERNAL ERROR : Unhandled configuration for children of a NonTerminal")
            print('')
            print(f"  path :  ", end='')
            _path = path + [node.name]
            prefix = ''
            for idx in range(len(_path)):
                i = ' ' * 3 * idx
                print(f"{prefix}{i}{_path[idx]}")
                prefix = ' ' * 10
            print('')
            print(f"  node = {node.name} : depth {depth}")
            seq = isinstance(children, Sequence)
            seq_text = ': is a sequence' if seq else ''
            print(f"  children type     = {str(type(children))} {seq_text}")
            if seq:
                print(f"  children[0] type  = {str(type(children[0]))}")
            print(": children =")
            pp(children)
            print(f"Please report this scenario to the maintainer.")
            out = Terminal(node.rule, 0, wrap(children))
            dprint(f": visit : {node.name} => {_res(out)}")
            dprint('')
            return out

    #--------------------------------------------------------------------------

    def empty(self, node, children):
        return None

    #--------------------------------------------------------------------------

    # A 'terminal' being, obviously, a Terminal node, contents in node.value
    def divulge_terminal ( self, node, children ):
        """ Dispense with an unneeded Terminal enclosing a value.  Sanity
	checks may result in a automatci divulge upgrade (i.e. if it is not
	actually a Terminal node (but not quietly).
	"""
        context = 'divulge_terminal'

        dprint(f": {context} : {node.name} : value = {node.value}")

        if False :
            # Academic Research Mode - every step must be perfect
            assert isinstance(node, Terminal), \
                internal_error(context, node, "is not a Terminal node")
            assert len(children) == 0, \
                internal_error(context, node, "Is Terminal with children ?")
        else :
            # Battle Mode -- keep going at all cost !  With some complaints ...
            upgrade = False
            if not isinstance(node, Terminal):
                internal_error(context, node, "Is not a Terminal node.")
                upgrade = True
            else :
                n = len(children)
                if n > 0:
                    internal_error(context, node, f"How does a Terminal have {n} children ?")
                    upgrade = True
            if upgrade:
                return self.divulge_single(node, children)

        dprint(f": {context} : '{node.name}' => {_res(node.value)}")
        # Intentially breaks the Parse Tree structure so that the parent or
        # other ancestor may trivially gather it's components.  Said gatherer
        # must have a visitor method of course.  text() is use to gather
        # text fragments into 
        
        return node.value

    #--------------------------------------------------------------------------

    def divulge_NonTerminal ( self,
                              context : str,
                              node : ParseTreeNode,
                              children : list,
                              only_child : bool ):

        """Sanity checks for a NonTerminal being 'divulged'.  Automatically
	upgrades or downgrades the divulge action as necessary (with complaints).
	"""

        # Battle Mode -- keep going at all costs -- with noisy complaints for improvement ...

        if not isinstance(node, NonTerminal):
            internal_error(context, node, "Is not a NonTerminal node.  Perhaps it is a list ?")
            if not isinstance(node, list):
                internal_error(context, node, "Also not list.")
                if isinstance(node, Terminal):
                    internal_error(context, node, "It is a Terminal.  Downgrading automatically.")
                    return self.divulge_terminal(node, children)

        if only_child and len(children) > 1:
            internal_error(context, node, f"Too many children.  Upgrading automatically.")
            return self.divulge_list(node, children)

        if len(children) <= 0:
            internal_error(context, node, f"How does a NonTerminal have ZERO children ?  "
                           "Let's try handling it like a Terminal.")
            w = wrap(node.value)
            dprint(f": {context} : '{node.name}' => {_res(w)}")
            return w

        return None

    #--------------------------------------------------------------------------

    # A 'single' being a NonTerminal with only one child, a ParseTreeNode
    def divulge_single ( self, node, children ):
        """ Dispense with an unneeded NonTerminal enclosing a single node."""
        context = 'divulge_single'

        out = self.divulge_NonTerminal(context, node, children, only_child=True)
        if out is not None:
            return out

        single = children[0]
        if isinstance(single, ParseTreeNode):
            internal_error(context, node, f"And it's single child is not ParseTreeNode.  "
                           "We'll simply let that slide.")
        w = wrap(single)
        dprint(f": divulge single '{node.name}' => {_res(w)}")
        return w

    #--------------------------------------------------------------------------

    def divulge_list ( self, node, children ):
        """ Dispense with an unneeded NonTerminal enclosing a 'list' of one
        or more nodes.  Though, if it can only ever have one child,
        divulge_single() would be more appropriate.
	"""
        context = 'divulge_list'

        out = self.divulge_NonTerminal(context, node, children, only_child=False)
        if out is not None:
            return out

        if isinstance(children[0], ParseTreeNode):
            internal_error(context, node, f"And it's first child is not ParseTreeNode.  "
                           "We'll simply let that slide.")

        w = wrap(children)
        dprint(f": {context} : '{node.name}' => {_res(w)}")
        return w

    #--------------------------------------------------------------------------

    # operand name is all that is relevant (i.e. FILE or <src>)
    def visit_operand(self, node, children):
        return Terminal(node.rule, 0, node.value)

    #--------------------------------------------------------------------------

    # make BAR directly searchable within the choice list
    def visit_BAR(self, node, children):
        return self.BAR

    def visit_choice(self, node, children):

        # *** Need to maintain valid Parse Tree, up one level ?
        # ***   >>> return sentinel indicating that visit should unwrap as
        # ***       children of choice's parent.

        # Eliminate fake choice, now must look into expressions
        #
        # XXX Test case 12 : 'Usage: copy move\ncopy ( move )'
        # XXX      output : error/name/lost-choice-and-expressions
        # XXX
        # XXX Error manifests without this enabled.
        #
        # This isn't the cause, it simply magnifies the error.
        #
        # Error is caused by the puzzling loss of the 'usage_pattern' enclosure
        # >>> unwrap() was doing too much unwrapping
        #
        if True :
            if ( len(children) == 1 and
                 isinstance(children[0], NonTerminal) and
                 children[0].rule_name == 'expression' and
                 self.BAR not in children[0] ) :
                return Unwrap(children[0])

        # Elimnate unnecessary expression wrapper when it has a single child
        #
        # *** If must be FALSE, document why and which test case
        #
        # >>> 'expression' context needful to discriminate between choice factors
        #
        if True :
            # DO NOT ENABLE THIS for now
            for idx in range(len(children)):
                child = children[idx]
                if  ( isinstance(child, NonTerminal) and
                      child.rule_name == 'expression' and
                      len(child) == 1 ) :
                    children[idx] = child[0]

        # Unchain cascading choices -- only necessary if recursive
        #   i.e. choice = expression ( BAR choice )
        #
        # NO LONGER NEEDED:  choice = expression ( BAR expression )*
        #
        if False and ( isinstance(children, list) and len(children) == 3
             and isinstance(children[-1], list) and children[-1][0] ):
            additional = children[-1]
            del children[-1]
            children.extend(additional)

        return NonTerminal(node.rule, children)

    #--------------------------------------------------------------------------

    #example #EXAMPLE
    def visit_Non_Terminal ( self, node, children ):
        return NonTerminal(node.rule, children)

    #--------------------------------------------------------------------------

    def visit_options_intro(self, node, children):
        # print(f": visit_options_intro : {node.name}")
        # pp(children)
        return Terminal(node.rule, 0, '\n'.join(children))

    def visit_operand_intro(self, node, children):
        # print(f": visit_operand_intro : {node.name}")
        # pp(children)
        return Terminal(node.rule, 0, '\n'.join(children))

    def _visit_operand_help(self, node, children):
        while isinstance(children[-1], list):
            tmp = children[-1]
            children = children[:-1]
            children.extend(tmp)
        return Terminal(node.rule, 0, '\n'.join(children))

    def _visit_option_help(self, node, children):
        print(f": visit_option_help : {node.name}")
        pp(children)
        while isinstance(children[-1], list):
            additional = children[-1]
            children = children[:-1]
            children.extend(additional)
        if isinstance(children[-1], Terminal):
            children[-1] = children[-1].value
        return Terminal(node.rule, 0, '\n'.join(children))

    #--------------------------------------------------------------------------

    def text(self, node, children):
        # print(f": text : {node.rule_name} : len = {len(children)}")
        # example: option_help = words ( newline !option_single option_help )*
        if isinstance(children[-1], Terminal):
            children[-1] = children[-1].value
        else:
            # example: intro = newline* !usage_entry line+ newline
            while isinstance(children[-1], list):
                additional = children[-1]
                children = children[:-1]
                children.extend(additional)
        return Terminal(node.rule, 0, '\n'.join(children))

    #--------------------------------------------------------------------------

    def visit_description(self, node, children):
        return Terminal(node.rule, 0, '\n'.join(children))

    def visit_line(self, node, children):
        assert len(children) == 1
        return children[0]

    def visit_words(self, node, children):
        return ' '.join(children)

    def visit_word(self, node, children):
        return node.value

    #--------------------------------------------------------------------------

    visit_trailing = text

    def visit_trailing_line (self, node, children):
        assert len(children) == 1
        return children[0]

    def visit_trailing_strings(self, node, children):
        return ' '.join(children)

    def visit_string_no_whitespace(self, node, children):
        return node.value

#------------------------------------------------------------------------------

def _res(x, indent=''):
    # return ('\n'+x.tree_str()) if hasattr(x, 'tree_str') else x
    text = None
    if hasattr(x, 'tree_str'):
        try :
            text = x.tree_str()
        except :
            pass
    if text is None :
        # text = str(x)
        text = pp_str(x)
    if '\n' in text:
        newline = f"\n{indent}"
        text = newline + text.replace('\n', newline)
    return text

#------------------------------------------------------------------------------
