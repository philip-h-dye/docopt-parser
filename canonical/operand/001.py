from arpeggio import EOF, Optional, ZeroOrMore, OneOrMore
from arpeggio import RegExMatch as _

ALL = [ 'operand', 'operand_angled', 'operand_all_caps' ]

# def ws():		return _(r'[ \t\r]+')
# def wx():		return ZeroOrMore( ws )	# was '_' in PEG grammar

def operand_angled():	return _(r'<[-_:\w]+>')
def operand_all_caps():	return _(r'[A-Z][_A-Z0-9]+\b')
def operand():		return [ operand_angled , operand_all_caps ]

# Keep EOF termination so that the bulk of the grammar my be reused.
def grammar():		return operand, EOF
