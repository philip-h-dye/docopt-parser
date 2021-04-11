# -*- coding: utf-8 -*-

import re

from setuptools import setup
from setuptools.command.install import install as InstallCommand

#------------------------------------------------------------------------------

class PreInstallCommand(InstallCommand):
    """DO NOT INSTALL -- Exploratory Only -- A Pre-installation for installation mode."""
    def run(self):
        # PUT YOUR PRE-INSTALL SCRIPT HERE or CALL A FUNCTION
        if False :
            install.run(self)
        # PUT YOUR POST-INSTALL SCRIPT HERE or CALL A FUNCTION

#------------------------------------------------------------------------------

_version = re.search("^__version__\s*=\s*'(.*)'",
                     open('test_.py').read(),
                     re.M ).group(1)

with open('README.rst', 'rb') as f:
    _long_description = f.read().decode('utf-8')

setup(
    name = 'usage_grammar',
    version = _version,
    description = "Exploratory PEG Grammar for docopt style usaged text.",
    author = 'Philip H. Dye',
    author_email = 'philip@phd-solutions.com',
    # url = 'http://www.phd-solutions.com/philip-d-dye',
    long_description = _long_description,
    py_modules=[], # none
    cmdclass={
        'install': PreInstallCommand,
    },
)

#------------------------------------------------------------------------------
