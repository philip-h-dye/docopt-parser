#------------------------------------------------------------------------------
# TODO
#   option-list
#   option-help
#   option-default
#------------------------------------------------------------------------------
# Simplify option-arguments.  If not directly, adjacent w/o whitespace,
# operands are just plain operands.  Whether a given operand should
# be a option-argument is left to semantic analysis.  Semantic analysis
# has to verify all of the details regardless of what does 'favored'
# approach is chosen in parsing.

# The parsing goal is not to glean every possible detail from a successful
# parse.  But rather to successfully parse valid AND INVALID language in
# order to serve the user best.  In semantic analysis, valid language is
# correlated and resolved to provide the details to program for use.  In
# the invalid case, semantic analysis should provide the user detailed
# information on why the provided language is invalid and, if feasible,
# steps that might be taken to resolve the issue I 

# Don't try to sqeeze all aspects out during parse.  A simpler,
# mostly-correct, successful parse is better than any failed parse.

import re

from arpeggio import EOF, Optional, ZeroOrMore, OneOrMore, RegExMatch
from arpeggio import OrderedChoice, Sequence, ZeroOrMore
from arpeggio import RegExMatch as _

from .common import EQ, ws # , wx
from .operand import operand

ALL = ( ' short_no_arg '
        ' long_no_arg '
        ' option_list ol_first_option ol_element '
        ' ol_option_lead ol_long ol_short  '
        ' _long _short '
        ' ol_operand_lead ol_operand'
       ).split()

#------------------------------------------------------------------------------

# Facilitate combining RegExMatch expressions by separating the leading
# and trailing constraints.
class RegExMatchBounded(RegExMatch):
    def __init__ (self, *args, lead : str = '', trail : str = '', **kwargs):
        super().__init__(*args, **kwargs)
        self.to_match_lead = lead       # generally a lookbehind
        self.to_match_trail = trail     # generally a lookahead

    def compile(self):
        # Only to get the flags :(
        super().compile()
        self.to_match_regex_bounded = ( self.to_match_lead +
                                        self.to_match_regex +
                                        self.to_match_trail )
        self.regex = re.compile(self.to_match_regex_bounded, self.regex.flags)

#------------------------------------------------------------------------------

# Punctuation in long and short args, numerous programs use punctuation
# in short or long args, embeded dash and underscore being the most
# common.  [:graph:] seems to make the most sense.  Though perhaps
# less dividing characters '|', ','.  Certainly not '='.

# Consider supporting customization of the option regexes.  Arpeggio's
# class customization technique might be a good model.

if True :
    def long_no_arg():
        return RegExMatchBounded \
            ( r'--[\w][\w]+', lead=r'(^|(?<=\s))', trail=r'\b',
              rule_name='long_no_arg', skipws=False )

    def short_stacked():
        return RegExMatchBounded \
            ( r'-[\w][\w]+', lead=r'(^|(?<=\s))', trail=r'\b',
              rule_name='short_stacked', skipws=False )

    def short_no_arg():
        return RegExMatchBounded \
            ( r'-[\w]', lead=r'(^|(?<=\s))', trail=r'\b',
              rule_name='short_no_arg', skipws=False )

    def long_eq_arg():
        """long argument, equal sign and operand:
              --file=foobar.txt (no gap around '=')
        """
        # Possible drawbacks with PEG is partial match might preclude backtracking ?
        # return Sequence ( ( long_no_arg, EQ, operand ),
        #                   rule_name='long_eq_arg', skipws=False )
        # FIXME:  Create composite from to_match attributes of
        #         long_no_arg() and operand().
        return RegExMatchBounded \
            ( r'--(?P<option>[\w][\w]+)' '=' r'(?P<operand>(<[-_:\w]+>|[A-Z][A-Z]+))',
              lead=r'(^|(?<=\s))', trail=r'\b',
              rule_name='long_eq_arg', skipws=False )

    def short_adj_arg():
        """short with directly adjacent operand, i.e. -fFILE or -f<file>"""
        return RegExMatchBounded \
            ( r'--(?P<option>[\w])' r'(?P<operand>[A-Z][A-Z]+)',
              lead=r'(^|(?<=\s))', trail=r'\b',
              rule_name='short_adj_arg', skipws=False )

if False :
    def long_no_arg():
        return _(r'(^|(?<=\s))--[\w][\w]+\b',
                  rule_name='long_no_arg', skipws=False)
    def short_stacked():
        return _(r'(^|(?<=\s))-[\w][\w]+\b',
                  rule_name='short_stacked', skipws=False)
    def short_no_arg():
        return _(r'(^|(?<=\s))-[\w]',
                  rule_name='short_no_arg', skipws=False)

if False :
    # Defer exploring the ramifications of this until the parser is working.
    def long_no_arg():
        return _( r'(^|(?<=[\s|,]))--(?!-=)[[:graph:]]((?!-=)[[:graph:]]))+',
                  rule_name='long_no_arg', skipws=False)
    def short_stacked():
        return _(r'(^|(?<=[\s|,]))-(?!-)[[:graph:]]+',
                  rule_name='short_stacked', skipws=False)
    def short_no_arg():
        return _(r'(^|(?<=[\s|,]))-(?!-)[[:graph:]]',
                  rule_name='short_no_arg', skipws=False)

#------------------------------------------------------------------------------

# option-description section
#   option-intro-line
#   options-descriptions
#     option-description-line
#       \s*<option-list>\s\s<option-help>
#         option-list
#           ( ( long-adj-arg | short-adj-arg ) \
#             [ long-adj-arg short-adj-arg operand ws = | , other ]* )
#               ^^^ the atoms or terms

_short = short_no_arg
_long = long_no_arg

def ol_element():
    return OrderedChoice( [ long_eq_arg, short_adj_arg short_stacked,
                            _long, _short,
                            rule_name='ol_element', skipws=False )

def ol_first_option():
    return Sequence ( ( And(ws), OrderedChoice( [ _long, _short ] ) ),
                      rule_name='ol_first_option', skipws=False )
    
def option_list():
    return Sequence( ( ol_first_option, ZeroOrMore(ol_element) ),
                     rule_name='option_list', skipws=False )

#------------------------------------------------------------------------------
