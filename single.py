#!/usr/bin/env python3

import json

from tatsu import parse
from tatsu.util import asjson


slurp = lambda filename : [(f.read(), f.close()) for f in [open(filename,'r')]][0][0]

GRAMMAR = slurp("unix-utility-usage.peg")

_indent = 4

usage = 'Usage: hello -abc --why <file>'
usage = 'Usage: hello <file>'

ast = parse(GRAMMAR, usage)

print(json.dumps(asjson(ast), indent=_indent))

#
