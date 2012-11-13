
import os
import unittest

tests_dir = os.path.abspath(os.path.dirname(__file__))

loader = unittest.TestLoader()
tests = loader.discover(tests_dir)

suite = unittest.TestSuite()
suite.addTests(tests)
