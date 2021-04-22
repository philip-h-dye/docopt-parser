import arpeggio

from prettyprinter import register_pretty, pretty_call, cpprint as pp

#------------------------------------------------------------------------------

# for shorter names when printing

class NonTerminal (object): pass
class Terminal (object): pass
class SemanticActionResults(object): pass

#------------------------------------------------------------------------------

@register_pretty(arpeggio.NonTerminal)
def pretty_NonTerminal(value, ctx):
    return pretty_call(
        ctx,
        NonTerminal,
        rule_name=value.rule_name,
        # value=value.value,
        contents=list(value),
    )

@register_pretty(arpeggio.Terminal)
def pretty_Terminal(value, ctx):
    return pretty_call(
        ctx,
        Terminal,
        rule_name=value.rule_name,
        value=value.value,
    )

@register_pretty(arpeggio.SemanticActionResults)
def pretty_SemanticActionResults(value, ctx):
    return pretty_call(
        ctx,
        SemanticActionResults,
        rule_name=value.rule_name,
        contents=list(value),
    )

#------------------------------------------------------------------------------
