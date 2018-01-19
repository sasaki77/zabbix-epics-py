#!/usr/bin/env python

import unittest
from zbxepics.casender.zbxmath import last, avg


class TestZabbixMath(unittest.TestCase):

    def test_last_value(self):
        vals = [v for v in range(10)]
        last_val = last(vals)
        self.assertEqual(last_val, 9)

    def test_last_err(self):
        with self.assertRaises(IndexError):
            vals = []
            last(vals)

    def test_average_value(self):
        vals = [v for v in range(10)]
        avg_val = avg(vals)
        self.assertEqual(avg_val, 4.5)

    def test_average_err(self):
        with self.assertRaises(ZeroDivisionError):
            vals = []
            avg(vals)


def main():
    unittest.main(verbosity=2)


if __name__ == '__main__':
    main()
