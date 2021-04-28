from arpeggio import OrderedChoice, RegExMatch as _

from .common import ws

ALL = [ 'operand', 'operand_angled', 'operand_all_caps' ]

def operand_angled():	return _(r'<[-_:\w]+>')

def operand_all_caps():	return _(r'[A-Z][_A-Z0-9]+\b')

def operand():
    return OrderedChoice( [ operand_angled , operand_all_caps ],
                          rule_name='operand', skipws=False )
