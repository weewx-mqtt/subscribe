#    Copyright (c) 2025 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#

# pylint: disable=missing-module-docstring, missing-class-docstring, missing-function-docstring

import importlib
import random
import string
import sys
import unittest

def random_string(length=32):
    return ''.join([random.choice(string.ascii_letters + string.digits) for n in range(length)])


def run_tests():
    if len(sys.argv) == 1:
        unittest.main(exit=False)
        exit()
    elif len(sys.argv) == 3:
        filename = sys.argv[0].rsplit('/', 1)[-1]
        module_name = filename.split('.', 11)[0]
        module = importlib.import_module(module_name)

        test_class = getattr(module, sys.argv[1])

        test_suite = unittest.TestSuite()
        test_suite.addTest(test_class(sys.argv[2]))
        unittest.TextTestRunner().run(test_suite)
        exit()

    print("Bad parameters")
