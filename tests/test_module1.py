# tests/test_module1.py

import unittest
from project_name.module1 import Calculator

class test_Calculator(unittest.TestCase):

    def setUp(self):
        self.calc = Calculator()

    def test_add(self):
        self.assertEqual(self.calc.add(2, 3), 5)
        self.assertEqual(self.calc.add(-1, 1), 0)

    def test_subtract(self):
        self.assertEqual(self.calc.subtract(10, 5), 6)
        self.assertEqual(self.calc.subtract(-1, -1), 0)

if __name__ == '__main__':
    unittest.main()
