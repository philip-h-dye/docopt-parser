#

test_cases = [
    'Usage:  hello FILE',
    'Usage:  hello FILE PLAN NAME <name> <file> <task>',
    "Usage:  my_program command --option <argument>",
    'Usage:  hello -abc --why <file>',
    #
    "Usage:  my_program [<optional-argument>]",
    "Usage:  my_program --another-option=<with-argument>",
    "Usage:  my_program (--either-that-option | <or-this-argument>)",
    "Usage:  my_program <repeating-argument> <repeating-argument>...",
    """Usage:
         qq_program command --option <argument>
         my_program [<optional-argument>]
         my_program --another-option=<with-argument>
         my_program (--either-that-option | <or-this-argument>)
         my_program <repeating-argument> <repeating-argument>..,
    """,
    "Usage:  my_program commandx -a -b -c <argument> \n",
    "Usage:  my_program commandx -abc <argument> \n",
    "Usage:  my_program commandx --long <argument> \n",
    "Usage:  my_program commandx --long= <argument> \n",
    "Usage:  my_program commandx --long=<argument> \n",
    "Usage:  my_program commandx --option <argument>",
    "Usage:  my_program NORM <positional-argument> \n",
    "Usage:  my_program NORM <positional-argument> [<optional-argument>] \n",
    "Usage:  my_program --another-option=<with-argument>",
    "Usage:  my_program (--either-that-option | <or-this-argument>)",
    "Usage:  my_program <repeating-argument> <repeating-argument>...",
]

#
