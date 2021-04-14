import parsimonious

#------------------------------------------------------------------------------
if False :
    import sys
    print(': import paths')
    for path in sys.path :
        print(path)
    print(': - - - - -')
    print('')
    sys.stdout.flush()
#------------------------------------------------------------------------------

GRAMMAR_FILE = 'docopt.peg'

# USAGE_PATTERN = "hello = 5"
# USAGE_PATTERN = "Usage:  hello = 5"
# USAGE_PATTERN = "Usage:"
# USAGE_PATTERN = "Usage:  hello-world"
# USAGE_PATTERN = "Usage:  hello-world FILE <another-argument>"
# USAGE_PATTERN = "Usage:  convoy Move-Forward FILE <another-argument>"
# USAGE_PATTERN = "Usage:  convoy --why"
# USAGE_PATTERN = "Usage:  convoy -a --why -b --what"
# USAGE_PATTERN = "Usage:  convoy Move-Forward --why FILE <another-argument>"
# USAGE_PATTERN = "Usage:  convoy Move-Forward -a -b -c --why FILE <another-argument>"

# USAGE_PATTERN = "Usage:  convoy [<another-argument>]"

# USAGE_PATTERN = "Usage:  program FILE <dst>"

# New approach : model on SMILE 'Simplify' Stage
#   1. atoms
#   2  expressions of single atoms
#   3. expressions of sequences of atoms

# Starting from SMILE 'Simplify', USAGE_PATTERN ="3+4"
# USAGE_PATTERN =" FILE "
# USAGE_PATTERN =" 	FILE \n"		# this \b is bell  : works

# USAGE_PATTERN =" 	\bFILE \n"		# this \b is bell  : this fails !
#						# bell isn't whitespace, not an issue

# USAGE_PATTERN = "<another-argument>"
# USAGE_PATTERN =" <another-argument> 	\n"

USAGE_PATTERN ="  [ FILE ]  "
# USAGE_PATTERN =" 	[FILE] "
# USAGE_PATTERN = "[<another-argument>]"
# USAGE_PATTERN = "[FILE + <another-argument>]"
# USAGE_PATTERN = "FILE <another-argument>"
# USAGE_PATTERN = "[ FILE <another-argument> ]"

#------------------------------------------------------------------------------

def to_str(node):
    if node.children:
        return ''.join([to_str(child) for child in node])
    else:
        return node.text

#------------------------------------------------------------------------------

slurp = lambda fname : [(f.read(), f.close()) for f in [open(fname,'r')]][0][0]

if True :
    grammar = slurp(GRAMMAR_FILE)
    g = parsimonious.Grammar(grammar)
else :
    import bootstrap
    g = bootstrap.docopt_grammar

AST = g.parse(USAGE_PATTERN)

# print( '    ' + str(eval(to_str(AST))) )
# print( '    ' + to_str(AST) )
print( AST )

#------------------------------------------------------------------------------
