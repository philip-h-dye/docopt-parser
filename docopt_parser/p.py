import io

from contextlib import redirect_stdout

from prettyprinter import register_pretty, pretty_call, cpprint as pp

import arpeggio

# from arpeggio import EOF, Optional, ZeroOrMore, OneOrMore
# from arpeggio import And, Not, StrMatch, RegExMatch as _

#------------------------------------------------------------------------------

def pp_str(obj):
    sio = io.StringIO()
    with redirect_stdout(sio):
        pp(obj)
    return sio.getvalue()

#------------------------------------------------------------------------------

# Use shorter names when printing

class NonTerminal (object): pass
@register_pretty(arpeggio.NonTerminal)
def pretty_NonTerminal(value, ctx):
    return pretty_call(
        ctx,
        NonTerminal,
        rule_name=value.rule_name,
        # value=value.value,
        contents=list(value),
    )

class Terminal (object): pass
@register_pretty(arpeggio.Terminal)
def pretty_Terminal(value, ctx):
    return pretty_call(
        ctx,
        Terminal,
        # rule_type=str(type(value.rule)),
        rule_name=value.rule_name,
        value=value.value,
    )

class SemanticActionResults (object): pass
@register_pretty(arpeggio.SemanticActionResults)
def pretty_SemanticActionResults(value, ctx):
    return pretty_call(
        ctx,
        SemanticActionResults,
        rule_name=value.rule_name,
        contents=list(value),
    )

#------------------------------------------------------------------------------

class EOF: pass
@register_pretty(arpeggio.EOF)
def pretty_EOF(value, ctx):
    return pretty_call(
        ctx,
        EOF,
    )

class ParsingExpression: pass
@register_pretty(arpeggio.ParsingExpression)
def pretty_ParsingExpression(value, ctx):
    return pretty_call(
        ctx,
        ParsingExpression,
        name = value.name,
        # desc = value.desc,
        rule_name = value.rule_name,
        elements = value.elements,
        root = value.root,
        # nodes = value.nodes,
        # supress = value.supress,
    )

class StrMatch: pass
@register_pretty(arpeggio.StrMatch)
def pretty_StrMatch(value, ctx):
    return pretty_call(
        ctx,
        StrMatch,
        name = value.name,
        # desc = value.desc,
        rule_name = value.rule_name,
        # elements = value.elements,
        # root = value.root,
        # nodes = value.nodes,
        to_match = value.to_match,
        ignore_case = value.ignore_case,
        # supress = value.supress,
    )

class RegExMatch: pass
@register_pretty(arpeggio.RegExMatch)
def pretty_RegExMatch(value, ctx):
    return pretty_call(
        ctx,
        RegExMatch,
        name = value.name,
        # desc = value.desc,
        rule_name = value.rule_name,
        elements = value.elements,
        root = value.root,
        # nodes = value.nodes,
        to_match_regex = value.to_match,
        ignore_case = value.ignore_case,
        multiline = value.multiline,
        explicit_flags = value.explicit_flags,
        # supress = value.supress,
    )

class Sequence: pass
@register_pretty(arpeggio.Sequence)
def pretty_Sequence(value, ctx):
    return pretty_call(
        ctx,
        Sequence,
        name = value.name,
        # desc = value.desc,
        rule_name = value.rule_name,
        elements = value.elements,
        root = value.root,
        # nodes = value.nodes,
        ws = value.ws,
        skipws = value.skipws,
        # supress = value.supress,
    )

class UnorderedGroup: pass
@register_pretty(arpeggio.UnorderedGroup)
def pretty_UnorderedGroup(value, ctx):
    return pretty_call(
        ctx,
        UnorderedGroup,
        name = value.name,
        # desc = value.desc,
        rule_name = value.rule_name,
        elements = value.elements,
        root = value.root,
        # nodes = value.nodes,
        eolterm = value.eolterm,
        sep = value.sep,
        # supress = value.supress,
    )

class OrderedChoice: pass
@register_pretty(arpeggio.OrderedChoice)
def pretty_OrderedChoice(value, ctx):
    return pretty_call(
        ctx,
        OrderedChoice,
        name = value.name,
        # desc = value.desc,
        rule_name = value.rule_name,
        elements = value.elements,
        root = value.root,
        # nodes = value.nodes,
        # supress = value.supress,
    )

class Repetition: pass
@register_pretty(arpeggio.Repetition)
def pretty_Repetition(value, ctx):
    return pretty_call(
        ctx,
        Repetition,
        name = value.name,
        # desc = value.desc,
        rule_name = value.rule_name,
        elements = value.elements,
        root = value.root,
        # nodes = value.nodes,
        eolterm = value.eolterm,
        sep = value.sep,
        # supress = value.supress,
    )

class Optional: pass
@register_pretty(arpeggio.Optional)
def pretty_Optional(value, ctx):
    return pretty_call(
        ctx,
        Optional,
        name = value.name,
        # desc = value.desc,
        rule_name = value.rule_name,
        # elements = value.elements,
        root = value.root,
        # nodes = value.nodes,
        eolterm = value.eolterm,
        sep = value.sep,
        # supress = value.supress,
    )

class ZeroOrMore: pass
@register_pretty(arpeggio.ZeroOrMore)
def pretty_ZeroOrMore(value, ctx):
    return pretty_call(
        ctx,
        ZeroOrMore,
        name = value.name,
        # desc = value.desc,
        rule_name = value.rule_name,
        elements = value.elements,
        root = value.root,
        # nodes = value.nodes,
        eolterm = value.eolterm,
        sep = value.sep,
        # supress = value.supress,
    )

class OneOrMore: pass
@register_pretty(arpeggio.OneOrMore)
def pretty_OneOrMore(value, ctx):
    return pretty_call(
        ctx,
        OneOrMore,
        name = value.name,
        # desc = value.desc,
        rule_name = value.rule_name,
        elements = value.elements,
        root = value.root,
        # nodes = value.nodes,
        eolterm = value.eolterm,
        sep = value.sep,
        # supress = value.supress,
    )

class And: pass
@register_pretty(arpeggio.And)
def pretty_And(value, ctx):
    return pretty_call(
        ctx,
        And,
        name = value.name,
        # desc = value.desc,
        rule_name = value.rule_name,
        elements = value.elements,
        root = value.root,
        # nodes = value.nodes,
        # supress = value.supress,
    )

class Not: pass
@register_pretty(arpeggio.Not)
def pretty_Not(value, ctx):
    return pretty_call(
        ctx,
        Not,
        name = value.name,
        # desc = value.desc,
        rule_name = value.rule_name,
        elements = value.elements,
        root = value.root,
        # nodes = value.nodes,
        # supress = value.supress,
    )

class Empty: pass
@register_pretty(arpeggio.Empty)
def pretty_Empty(value, ctx):
    return pretty_call(
        ctx,
        Empty,
        name = value.name,
        # desc = value.desc,
        rule_name = value.rule_name,
        elements = value.elements,
        root = value.root,
        # nodes = value.nodes,
        # supress = value.supress,
    )

#------------------------------------------------------------------------------
