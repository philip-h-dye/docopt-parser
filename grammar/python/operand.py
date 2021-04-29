from arpeggio import OrderedChoice, RegExMatch as _

ALL = [ 'operand', 'operand_angled', 'operand_all_caps' ]

def operand_angled():
    return _(r'<[-_:\w]+>', rule_name='operand_angled')

def operand_all_caps():
    # '\b' is required to not improperly match 'FOO' of 'FOObar'
    return _(r'[A-Z][_A-Z0-9]+\b', rule_name='operand_all_caps')

def operand():
    return OrderedChoice( [ operand_angled , operand_all_caps ],
                          rule_name='operand', skipws=False )
