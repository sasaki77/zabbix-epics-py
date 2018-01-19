#!/usr/bin/env python

import unittest
from zbxepics.casender import ZabbixSenderItem
from zbxepics.pvsupport import ValQPV


class TestZabbixSenderItem(unittest.TestCase):

    def test_init_monitor(self):
        item = ZabbixSenderItem('host1', 'ET_dummyHost:ai1', 'monitor')
        self.assertEqual(item.host, 'host1')
        self.assertIsInstance(item.pv, ValQPV)
        self.assertEqual(item.pv.pvname, 'ET_dummyHost:ai1')
        self.assertEqual(item.interval, 'monitor')

    def test_init_interval(self):
        item = ZabbixSenderItem('host1', 'ET_dummyHost:ai1', 5, 'last')
        self.assertEqual(item.host, 'host1')
        self.assertIsInstance(item.pv, ValQPV)
        self.assertEqual(item.pv.pvname, 'ET_dummyHost:ai1')
        self.assertEqual(item.interval, 5)

    def test_init_err_invalid_interval(self):
        with self.assertRaises(Exception):
            ZabbixSenderItem('host1', 'ET_dummyHost:ai1', 'scan')

    def test_init_err_invalid_func(self):
        with self.assertRaises(Exception):
            ZabbixSenderItem('host1', 'ET_dummyHost:ai1', 5, 'add')

    def test_init_err_func_none(self):
        with self.assertRaises(Exception):
            ZabbixSenderItem('host1', 'ET_dummyHost:ai1', 5)

    def test_init_err_short_interval(self):
        with self.assertRaises(Exception):
            ZabbixSenderItem('host1', 'ET_dummyHost:ai1', 0.9, 'last')


def main():
    unittest.main(verbosity=2)


if __name__ == '__main__':
    main()
