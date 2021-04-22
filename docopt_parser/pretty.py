from arpeggio import Terminal, NonTerminal, SemanticActionResults

from prettyprinter import register_pretty, pretty_call

@register_pretty(SemanticActionResults)
def pretty_SemanticActionResults(value, ctx):
    return pretty_call(
        ctx,
        SemanticActionResults,
        rule_name=value.rule_name,
        contents=list(value),
    )

@register_pretty(NonTerminal)
def pretty_NonTerminal(value, ctx):
    return pretty_call(
        ctx,
        NonTerminal,
        rule_name=value.rule_name,
        # value=value.value,
        contents=list(value),
    )

@register_pretty(Terminal)
def pretty_Terminal(value, ctx):
    return pretty_call(
        ctx,
        NonTerminal,
        rule_name=value.rule_name,
        value=value.value,
        # contents=list(value),
    )
