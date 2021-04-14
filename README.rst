docopt-parser : Parser for the docopt language
======================================================================

*This is not usable in any form at the moment.*

STATUS:

The grammar is complete but in considerable testing remains.  And a
grammar is not the full story.  A semantic analysis pass is required
to sort out details that a grammar cannot.

4/14 Operand section (a.k.a. positional arguments) completed.

4/14 Now parsing usage patterns, program description and options section.

4/13 Made significant headway with usage pattern parsing.

4/12 Switched to arpeggio for its better debug info, see parser.py and
     docopt.peg.  Other python code is from prior PEG parser generator
     work that did not succeed.

-------------------------------

docopt language parser using a formal grammar.

The docopt language is being specified in a Parsing Expression Grammar (PEG) in order benefit from stadard tooling and better facilitate maintenance.

The docopt language details are as outlined on `docopt <http://docopt.org>`.  Itself a codification of prior practices of long standing.  Some UNIX/Linux standards bodies have laid out standards which might supplent that codified by docopt.

Things were moving quicky along, I hit my first mini-milestone by precisely parsing a modest variety of "Usage:" example lines only to encounter a serious technical glitch with the parser generator.

So, ratter moving on to milestone two, I am in the midst of migrating it to Parsimonious (PEG Parser Generator used by Wikipedia).  Odd that 'migration' is necessary given that they both well noted for being PEG parsers.  Significant syntax and grammsr differences must be sorted out.

Thus far, Parsimonious, appears to largely hold true to the PEG Grammar laid out by Bryan Ford in his paper noted beow.


It uses :

* `parsimonious <https://github.com/erikrose/parsimonious>`_
   Erik Rose's Parsimonious aims to be the fastest arbitrary-lookahead parser written in pure Python—and the most usable library for parsing using Parsing Expression Grammar (PEG) based upom the original paper by Bryan Ford'
  `Parsing Expression Grammars: A Recognition-Based Syntactic Foundation
  <http://pdos.csail.mit.edu/papers/parsing:popl04.pdf>`_.

* `py.test <http://pytest.org>`_ testing framework.
  (See also the book `Test-Driven Development: By Example
  <http://books.google.com/books/about/Test_Driven_Development.html?id=gFgnde_vwMAC>`_).
