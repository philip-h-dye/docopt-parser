from glob import glob

#------------------------------------------------------------------------------

slurp = lambda fname : [(f.read(), f.close()) for f in [open(fname,'r')]][0][0]

#------------------------------------------------------------------------------

pname_pattern = 'f"examples/usage/{pname}/doc.txt"'

def programs(pname='*'):

    return glob(eval(pname_pattern))

def program_usages():

    pname = '*'

    _programs = glob(eval(pname_pattern))

    for i in range(len(_programs)):
        _programs[i] = slurp(_programs[i])

    return _programs

#------------------------------------------------------------------------------

def general():
    return [ # 0
         #
         # usage pattern section -- the only required section
         #
           # basic usage patterns, simple arguments, all caps
             u"Usage: copy",
             u"Usage: copy FILE",
             u"Usage: copy SRC DST",
             u"Usage: copy SRC1 SRC2 DST",
             u"Usage: copy SRC1 SRC2 SRC3 DST",
           # basic usage patterns, options, implicit choice groupings
             u"Usage: copy -h",
             u"Usage: copy -h | --help",
             u"Usage: copy -h | --help | --also",
             # implicit choice must partition the line, one point where expression is crucial
             u"Usage: copy side-a -h | --help side-b",
             u"Usage: copy move fire -h | --help",
           # required
             # choice, first is fake since it is alone, others actual
             u"Usage: copy move ",		# implicit and explicit required
             u"Usage: copy ( move ) ",		# must parse identically
             u"Usage: copy move\n  copy ( move ) ",
             u"Usage: copy ( move | fire )",
             u"Usage: copy ( move | fire | turn )",
             u"Usage: copy ( move | fire | turn | fire )",
             # actual choice followed by both implied and explicit required
             u"Usage: copy ( move | fire ) turn rise",
             u"Usage: copy ( move | fire ) ( turn rise )",
             # two pairs of actual choice
             u"Usage: copy ( move | fire ) ( turn | rise )",
             # embedded choices
             u"Usage: copy ( ( move | fire ) | ( turn | rise ) )",
             u"Usage: copy ( ( move | fire ) | turn )",
             u"Usage: copy ( move | ( fire | turn ) )",
             u"Usage: copy ( move | ( fire | ( turn | rise ) ) )",
           # optional
             # choice, first is fake since it is alone, others actual
             u"Usage: copy [ move ] ",
             u"Usage: copy [ move | fire ]",
             u"Usage: copy [ move | fire | turn ]",
             u"Usage: copy [ move | fire | turn | fire ]",
             # actual choice followed by both implied and explicit required
             u"Usage: copy [ move | fire ] turn rise",
             u"Usage: copy [ move | fire ] [ turn rise ]",
             # two pairs of actual choice
             u"Usage: copy [ move | fire ] [ turn | rise ]",
             # embedded choices
             u"Usage: copy [ [ move | fire ] | [ turn | rise ] ]",
             u"Usage: copy [ [ move | fire ] | turn ]",
             u"Usage: copy [ move | [ fire | turn ] ]",
             u"Usage: copy [ move | [ fire | [ turn | rise ] ] ]",
             # 
           # multiple usage patterns
             u"Usage: copy1 \n copy2 \n\n",
             u"Usage: copy1 \n copy2 \n copy3 ",
             u"Usage: copy1 FILE \n copy2 FILE \n\n",
             u"Usage: copy1 FILE \n copy2 FILE \n copy3 FILE ",
             # OR between usage lines
             u"Usage: copy1 FILE \n or copy2 FILE \n",
             u"Usage: copy1 FILE \n or copy2 FILE \n or copy3 FILE \n",
           # options
             u"Usage: move -a",
             u"Usage: move -a -b",
             u"Usage: move -a -b -c",
             u"Usage: move -a -b -c -d",
             u"Usage: move -ab",
             u"Usage: move -abc",
             u"Usage: move -abcd",
             u"Usage: move --one",
             u"Usage: move --one --two",
             u"Usage: move --one --two --three",
             u"Usage: move --one --two --three --four",
           # repeating
             # 49
             u"Usage: copy <move>... ",
             u"Usage: copy <move> <move>... ",
             u"Usage: copy ( move [ fire ]... )...",
           # double-dash '--'
             u"Usage: my_program [options] [--] <file>...",
           # single dash '[-]', file input from stdin
             u"Usage: copy [options] ( <file>... | - )",
           # combinations
             u"Usage: test [mode] TARGET\n\n  Xy a program to ",
             u"Usage: copy -l\n\n Test program \n",
             u"Usage: copy [ --speed <speed> --angle ANGLE ] <when>",
             u"Usage: copy -abc --why <file>",
             u"Usage:  my_program command --option <argument>",
             u"Usage:  my_program [<optional-argument>]",
             u"Usage:  my_program --another-option=<with-argument>",
             u"Usage:  my_program (--either-that-option | <or-this-argument>)",
             u"Usage:  my_program <repeating-argument> <repeating-argument>...",
           # 63
             """Usage:
	         my_program command --option <argument>
	         my_program [<optional-argument>]
	         my_program --another-option=<with-argument>
	         my_program (--either-that-option | <or-this-argument>)
	         my_program <repeating-argument> <repeating-argument>...
	     """,
             u"Usage:  my_program commandx -a -b -c <argument> \n",
             u"Usage:  my_program commandx -abc <argument> \n",
             u"Usage:  my_program commandx --long <argument> \n",
             u"Usage:  my_program commandx --long= <argument> \n",
             u"Usage:  my_program commandx --long=<argument> \n",
             u"Usage:  my_program commandx --option <argument>",
             u"Usage:  my_program NORM <positional-argument> \n",
             u"Usage:  my_program NORM <positional-argument> [<optional-argument>] \n",
             u"Usage:  my_program --another-option=<with-argument>",
             u"Usage:  my_program (--either-that-option | <or-this-argument>)",
             u"Usage:  my_program <other> ( <a> | <b> ) ...",
	     u"Usage:  typo-example <repeating-typo-w-comma>..,",
             # '..,' => command due to typo, classic user error that should be
             #          provide a gentle reminder
             u"Usage:  my_program <repeating> <repeating>...",
             u"Usage:  my_program --flag <repeating> <repeating>... --what",
             # choice chain with implicit grouping
             u"Usage:  my_program --flag | --what | --now",
             u"Usage:  my_program ( --flag | --what | --now )",
             u"Usage:  my_program ( a b c )",
             # 1. fake choice in req grouping, 2. real choice in req grouping
             u"Usage:  my_program ( a b c ) ( --flag | --what | --now )",
             u"Usage:  my_program --flag <no-unexpected-grouping>",
             u"Usage:  my_program --flag <unexpected> <grouping>",
             # this calcultar pattern tripped a bug in a later version of the grammar
             u"Usage:  calculator_example.py <value> ( ( + | - | * | / ) <value> )...",
         #
         # description section
         #
             u"Usage: copy FILE \n\n Description single line",
             u"Usage: copy FILE \n\n Description line 1\nDescription line 2",
             """Usage: copy FILE

First description line 1\n First description line 2

Second description line 1\n Second description line 2
""",
         #
         # intro section
         #
             "Intro section\n\n Usage: copy FILE",
             ( "Intro - line 1\nFirst intro - line 2\n\n"
               "Usage: copy FILE" ),
             ( "Intro - line 1\nFirst intro - line 2\n\n"
               "Second intro - line 1\nSecond intro - line 2\n\n"
               "Usage: copy FILE" ),
             # 45
           ]

#------------------------------------------------------------------------------

def fragment():

    return [
        "Usage : copy SRC DST",
        "Usage : copy SRC DST \n move FROM TO",
        "Usage : copy SRC DST \n move FROM TO \n\n  Test program",
        """
Usage :
  copy [options] <src> <dst>

Test program
Line 2""",
        """
Usage :
  copy [options] <src> <dst>

Test program
Line 2

Positional Arguments :
  <src>         File to be copied
  <dst>         File to written""",
        """
Usage :
  copy [options] <src> <dst>

Test program Line 2
Second traditional description line.

Positional Arguments :
  <src>         File to be copied
  <dst>         File to written

Intervening description.

Options :
  -w<word>      Word ...
  --what=<q>    What ...
  -l, --list    List ...""",
        """
Usage :
  copy [options] <src> <dst>

Test program
Line 2

Positional Arguments :
  <src>         File to be copied
  <dst>         File to written

Intervening description.

Options :
  -w<word>      Word ...
  --what=<q>    What ...
  -l, --list    List ...

Trailing description.""",
        ]

#------------------------------------------------------------------------------

def trailing():
    return [
        """
Usage :
  copy

Options :
  <dll>         DLL ...

Trailing description.

""",
        """
Usage :
  copy

Traditional description.
Second traditional description line.

Positional Arguments :
  <dll>         DLL ...

Intervening description.

Options :
  -w<word>      Word ...

Trailing description.

"""
    ]

#------------------------------------------------------------------------------
