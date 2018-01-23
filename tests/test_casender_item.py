#!/usr/bin/env python

import unittest
from zbxepics.casender import ZabbixSenderItem
from zbxepics.casender import ZabbixSenderItemInterval
from zbxepics.pvsupport import ValQPV


class TestZabbixSenderItem(unittest.TestCase):

    def test_init_monitor(self):
        item = ZabbixSenderItem('host1', 'ET_dummyHost:ai1')
        self.assertEqual(item.host, 'host1')
        self.assertIsInstance(item.pv, ValQPV)
        self.assertEqual(item.pv.pvname, 'ET_dummyHost:ai1')

        metrics = item.get_metrics()
        self.assertEqual(len(metrics), 0)

    def test_init_interval(self):
        item = ZabbixSenderItemInterval('host1', 'ET_dummyHost:ai1',
                                        5, 'last')
        self.assertEqual(item.host, 'host1')
        self.assertIsInstance(item.pv, ValQPV)
        self.assertEqual(item.pv.pvname, 'ET_dummyHost:ai1')
        self.assertEqual(item.interval, 5)

        with self.assertRaises(Exception):
            item.get_metrics()

    def test_init_err_short_interval(self):
        with self.assertRaises(Exception):
            ZabbixSenderItemInterval('host1', 'ET_dummyHost:ai1',
                                     0.9, 'last')

    def test_init_err_invalid_func(self):
        with self.assertRaises(KeyError):
            ZabbixSenderItemInterval('host1', 'ET_dummyHost:ai1',
                                     5, 'add')


def main():
    unittest.main(verbosity=2)


if __name__ == '__main__':
    main()
