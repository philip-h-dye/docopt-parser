option = short EOF

short = short_w_arg / short_stacked / short_no_arg 

short_w_arg = short_no_arg operand_no_space

short_stacked = &ws _ r'-[\w][\w]+\b'

short_no_arg = &ws _ r'-[\w]'

// operand = _ ( operand_all_caps / operand_angled )
// operand_all_caps = ws operand_no_space_all_caps
// operand_angled = ws operand_no_space_angled

operand_no_space = ( operand_no_space_all_caps / operand_no_space_angled )
operand_no_space_all_caps = r'[A-Z][_A-Z0-9]+\b'
operand_no_space_angled = r'<[-_:\w]+>'

def ws():		return r'[ \t\r]+'
def wx():		return ZeroOrMore( ws )	# was '_' in PEG grammar

def short_no_arg():	return And(ws) , wx , r'-[\w]'

def number():     return _(r'\d*\.\d*|\d+')
def factor():     return Optional(["+","-"]), [number,
                          ("(", expression, ")")]
def term():       return factor, ZeroOrMore(["*","/"], factor)
def expression(): return term, ZeroOrMore(["+", "-"], term)
def calc():       return OneOrMore(expression), EOF
