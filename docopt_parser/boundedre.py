import re

from arpeggio import RegExMatch

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
