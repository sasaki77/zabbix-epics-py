#!/usr/bin/env python

import unittest
import os
import time
from epics import ca
from ioccontrol import IocControl
from zbxepics.casender import ZabbixSenderItem
from zbxepics.casender import ZabbixSenderItemInterval
from zbxepics.pvsupport import ValQPV
from zbxepics.casender.peekqueue import PriorityPeekQueue


class TestZabbixSenderItem(unittest.TestCase):

    def setUp(self):
        db_file = '/'.join([os.path.dirname(__file__), 'test.db'])
        ioc_arg_list = ['-m', 'head=ET_dummyHost', '-d', db_file]
        self.__iocprocess = IocControl(arg_list=ioc_arg_list)
        self.__iocprocess.start()
        sport = str(IocControl.server_port)
        os.environ['EPICS_CA_AUTO_ADDR_LIST'] = 'NO'
        os.environ['EPICS_CA_ADDR_LIST'] = 'localhost:{}'.format(sport)
        ca.initialize_libca()

    def tearDown(self):
        ca.finalize_libca()
        self.__iocprocess.stop()

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

    def test_monitor_item_metrics(self):
        item = ZabbixSenderItem('host1', 'ET_dummyHost:long1')

        pv = item.pv
        test_vals = [v for v in range(5)]
        for val in test_vals:
            pv.put(val, wait=True)
        time.sleep(.05)

        metrics = item.get_metrics()
        self.assertEqual(len(metrics), 5)

        for (zm, tval) in zip(metrics, test_vals):
            self.assertEqual(zm.host, item.host)
            self.assertEqual(zm.key, item.item_key)
            self.assertEqual(zm.value, str(tval))

    def test_interval_item_metrics(self):
        item = ZabbixSenderItemInterval('host1', 'ET_dummyHost:long1',
                                        10, 'last')

        runtime = int(time.time()) + item.interval

        pv = item.pv
        for val in range(5):
            pv.put(val, wait=True)
        time.sleep(.05)

        # Wait until runtime is reached
        while True:
            now = int(time.time())
            if now >= runtime:
                break
            time.sleep(1)

        metrics = item.get_metrics()
        self.assertEqual(len(metrics), 1)

        for zm in metrics:
            self.assertEqual(zm.host, item.host)
            self.assertEqual(zm.key, item.item_key)
            self.assertEqual(zm.value, '4')


def main():
    unittest.main(verbosity=2)


if __name__ == '__main__':
    main()
