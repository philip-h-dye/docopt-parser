#!/usr/bin/env python3

import sys
import re
import unittest
import pytest
import json

import tatsu
from tatsu.util import asjson

from test_case_data import test_cases

#------------------------------------------------------------------------------

slurp = lambda filename : [(f.read(), f.close()) for f in [open(filename,'r')]][0][0]

GRAMMAR_FILE = 'unix-utility-usage.peg'

#------------------------------------------------------------------------------

@pytest.fixture(scope="session")
def session_tatsu_model():
    GRAMMAR = slurp(GRAMMAR_FILE)
    return tatsu.compile(GRAMMAR, "Unix Utility Command Syntax")

@pytest.fixture(scope="class")
def class_tatsu_model(request, session_tatsu_model):
    request.cls.tatsu_model = session_tatsu_model

#------------------------------------------------------------------------------

_indent = 4

@pytest.mark.usefixtures("class_tatsu_model")
class Test_Case ( unittest.TestCase ):

    def check_doc_string(self, usage):
        ast = self.tatsu_model.parse('Usage: hello -abc --why <file>')
        print(json.dumps(asjson(ast), indent=3))
        assert True, "The parse succeeded."

#------------------------------------------------------------------------------

n = 0

def get_test_name(usage):
    global n
    n += 1
    name = f"test_{n:003}_{usage}"
    name = _usage.sub('', name)
    name = name.replace(' .-<>()[]|\n','__')
    return _underscores.sub('_', name)


def get_test_method(usage):
    def test_method(self):
        self.check_doc_string(usage)
    return test_method

#------------------------------------------------------------------------------

_usage = re.compile(r'(?i)^\s*usage:\s*')

_underscores = re.compile(r'_+')

for usage in test_cases :
    setattr(Test_Case, get_test_name(usage), get_test_method(usage))

#------------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()

#------------------------------------------------------------------------------
