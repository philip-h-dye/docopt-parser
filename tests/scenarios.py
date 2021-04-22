from glob import glob

#------------------------------------------------------------------------------

slurp = lambda fname : [(f.read(), f.close()) for f in [open(fname,'r')]][0][0]

#------------------------------------------------------------------------------

fname_pattern = 'f"examples/usage/{fname}/doc.txt"'

def files():

    fname = '*'

    return glob(eval(fname_pattern))

def file_usages():

    fname = '*'

    files = glob(eval(fname_pattern))

    for i in range(len(files)):
        files[i] = slurp(files[i])

    return files

#------------------------------------------------------------------------------

def general():
    return [ # 0
             "Usage: copy",
             "Usage: copy SRC DST \n",
             "Usage: copy SRC DST \n move FROM TO \n",
             "Usage: copy -h | --help | --also",
             "Usage: copy ( move | fire | turn ) ",
             "Usage: copy ( move | fire ) ( turn rise )",
             "Usage: copy ( move | fire ) ( turn rise ) -h | --help",
             "Usage: copy ( move | fire | turn )",
             "Usage: copy [ move fire ]",
             "Usage: copy [ --what [ now ] ]" \
             # 10
             "Usage: copy1 \ncopy2 \n\n",
             "Usage: copy1 \n  copy2 \n  or copy3",
             "Usage: test [mode]",
             "Usage: test [mode] TARGET\n\n  Xy a program to ",
             "Usage: copy -l\n\n Test program \n",
             "Usage:  copy [ --speed <speed> --angle ANGLE ] <when>",
             "Usage:  copy -abc --why <file>",
             "Usage:  my_program command --option <argument>",
             "Usage:  my_program [<optional-argument>]",
             "Usage:  my_program --another-option=<with-argument>",
             # 20
             "Usage:  my_program (--either-that-option | <or-this-argument>)",
             "Usage:  my_program <repeating-argument> <repeating-argument>...",
             """Usage:
	         my_program command --option <argument>
	         my_program [<optional-argument>]
	         my_program --another-option=<with-argument>
	         my_program (--either-that-option | <or-this-argument>)
	         my_program <repeating-argument> <repeating-argument>...
	     """,
             "Usage:  my_program commandx -a -b -c <argument> \n",
             "Usage:  my_program commandx -abc <argument> \n",
             "Usage:  my_program commandx --long <argument> \n",
             "Usage:  my_program commandx --long= <argument> \n",
             "Usage:  my_program commandx --long=<argument> \n",
             "Usage:  my_program commandx --option <argument>",
             "Usage:  my_program NORM <positional-argument> \n",
             # 30
             "Usage:  my_program NORM <positional-argument> [<optional-argument>] \n",
             "Usage:  my_program --another-option=<with-argument>",
             "Usage:  my_program (--either-that-option | <or-this-argument>)",
             "Usage:  my_program <repeating-argument> <repeating-argument>...",
	     "Usage:  typo-example <repeating-typo-w-comma>..,",
             # '..,' => command due to typo, classic user error that should be
             #          provide a gentle reminder
             # 35
             "Usage:  my_program <repeating> <repeating>...",
             # 36
             "Usage:  my_program --flag <repeating> <repeating>... --what",
             # choice chain with implicit grouping
             "Usage:  my_program --flag | --what | --now",
             "Usage:  my_program ( --flag | --what | --now )",
             "Usage:  my_program ( a b c )",
             # 1. fake choice in req grouping, 2. real choice in req grouping
             "Usage:  my_program ( a b c ) ( --flag | --what | --now )",
             # 41
             "Usage:  my_program --flag <no-unexpected-grouping>", 
             "Usage:  my_program --flag <unexpected> <grouping>", 
             "Usage:  my_program --flag <unexpected> <grouping> <same-grouping>", 
             "Intro\n\nSecond intro\n\nUsage:  my_program --flag <unexpected> <grouping> <same-grouping>",
             #
             "Usage:  calculator_example.py <value> ( ( + | - | * | / ) <value> )...",
           ]

#------------------------------------------------------------------------------

def fragments():

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
