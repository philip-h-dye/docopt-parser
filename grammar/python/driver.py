#------------------------------------------------------------------------------
#
# doc is a line oriented language
#
#   The first non-whitespace characters on a line determine the
#   type of line.  The types are broken down below as 'sections'
#   but these are essentially logical grouping since, after the
#   usage section, the other sections may appear in any order
#   and any number of times.
#
#   Usage patterns lay down the fundamental forms allowed for
#   the command.  The option and operand descriptions provide
#   additional details to resolve ambiguities.  Or, when the
#   '[options]' shortcut is used, the option descriptions may
#   provide all of the option information for the command.
#
#   Command and action sections are not infrequently seen.
#   Further research is needed to see if a consensus has
#   arisen regarding a 'command'/sub-command/action shortcut(s)
#   to be implemented.  Considering a customization argument
#   for this.
#
#   Three sections simply gather text lines that aren't usage,
#   options or operands.
#
#   Logical sections are best clearly delineated by a blank line.
#   Unfortunately, mant developers have not adhered to this custom.
#
#------------------------------------------------------------------------------
#
# doc ->
#
#    intro-line*
#
#    usage-section ->
#       "Usage :"
#       usage-pattern +         # program, option, operand and other arguments
#
#    other-section *
#       option-description      # complement and/or complete operand details
#       operand-description     # a.k.a. positional-arguments
#       description             # free form text
#
#    trailing*                  # any trailing text -- catch all
#
#------------------------------------------------------------------------------

from usage import usage_section
from optdesc import option_description_section
from text import text_line

def intro_section():
    return Sequence( ( Not(option), Not(operand),
                       OneOrMore(text_line), ),
                     rule_name="intro_section", skipws=False )

def other_section():
    return OrderedChoice( [ description,
                            option_description_section,
                            operand_description_section, ],
                      rule_name="other_section", skipws=False )

def descripton():
    return Sequence( ( Not('Usage'), Not(option), Not(operand),
                       OneOrMore(text_line), ),
                     rule_name="description", skipws=False )

def trailing():
    return Sequence( ( OneOrMore( text_line ) ),
                     rule_name="trailing", skipws=False )

def docopt():
    return Sequence ( ( Optional(intro_section),
                        usage_section,
                        ZeroOrMore( other_section ),
                        trailing, ),
                      rule_name="docopt", skipws=False )
