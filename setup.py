# -*- coding: utf-8 -*-

import re

from setuptools import setup
from setuptools.command.install import install as InstallCommand

#------------------------------------------------------------------------------

class PreInstallCommand(InstallCommand):
    """DO NOT INSTALL -- This is NOT ready to be installed."""
    def run(self):
        # PUT YOUR PRE-INSTALL SCRIPT HERE or CALL A FUNCTION
        #  NO # install.run(self)
        # PUT YOUR POST-INSTALL SCRIPT HERE or CALL A FUNCTION
        pass

#------------------------------------------------------------------------------

slurp = lambda fname : [(f.read(), f.close()) for f in [open(fname,'r')]][0][0]

contents = slurp('src/docopt.peg')
vpattern = ".*//\s*__version__\s*=\s*[\"'](.*)[\"']"
_version = re.search ( vpattern, contents, re.M ).group(1)

with open('README.rst', 'rb') as f:
    _long_description = f.read().decode('utf-8')

#------------------------------------------------------------------------------

setup(
    name = 'docopt-parser',
    version = _version,
    description = "Exploratory PEG Grammar for docopt style usaged text.",
    author = 'Philip H. Dye',
    url = 'https://github.com/philip-h-dye/docpt-parser',
    long_description = _long_description,
    # py_modules=['docopt_parser'], # none yet
    cmdclass={
        'install': PreInstallCommand,
    },
)

#------------------------------------------------------------------------------
