#!/usr/bin/env python
"""Reference  pyepics/tests/pv_unittest.py"""

import unittest
from zbxepics.pvsupport import ValQPV


class TestValQPV(unittest.TestCase):

    def test_init(self):
        pv = ValQPV('ET_dummyHost:ai1')
        self.assertEqual(pv.pvname, 'ET_dummyHost:ai1')

    def test_init_err(self):
        with self.assertRaises(Exception):
            ValQPV()

    def test_queue_none(self):
        pv = ValQPV('ET_dummyHost:ai1')
        vals = pv.get_q_all()
        self.assertEqual(vals, [])


def main():
    unittest.main(verbosity=2)


if __name__ == '__main__':
    main()
