#!/usr/bin/env python

import unittest
import os
import time

from epics import ca, PV

from ioccontrol import IocControl
from zbxepics.casender.item import MonitorItemFactory, IntervalItemFactory
from zbxepics.casender.item.monitoritem import MonitorItem
from zbxepics.casender.item.intervalitem import IntervalItem


class TestZabbixSenderItem(unittest.TestCase):

    def setUp(self):
        dir_path = os.path.dirname(__file__)
        db_file = os.path.join(dir_path, 'test.db')
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

    def testA_init_monitor(self):
        item = (MonitorItemFactory
                .create_item('host1', 'ET_dummyHost:ai1'))

        self.assertIsInstance(item, MonitorItem)
        self.assertEqual(item.host, 'host1')
        self.assertIsInstance(item.pv, PV)
        self.assertEqual(item.pv.pvname, 'ET_dummyHost:ai1')

    def testA_init_interval(self):
        item = (IntervalItemFactory
                .create_item('host1', 'ET_dummyHost:ai1',
                                      5, 'last'))

        self.assertIsInstance(item, IntervalItem)
        self.assertEqual(item.host, 'host1')
        self.assertIsInstance(item.pv, PV)
        self.assertEqual(item.pv.pvname, 'ET_dummyHost:ai1')
        self.assertEqual(item.interval, 5)

    def testA_init_interval_default(self):
        item = (IntervalItemFactory
                .create_item('host1', 'ET_dummyHost:ai1'))

        default_interval = IntervalItem.DEFAULT_INTERVAL
        self.assertEqual(item.interval, default_interval)

        functions = IntervalItemFactory.list_of_functions()
        default_function = IntervalItemFactory.DEFAULT_FUNCTION
        self.assertEqual(type(item), functions[default_function])

    def test_monitor_item_metrics(self):
        item = (MonitorItemFactory
                .create_item('host1', 'ET_dummyHost:long1'))

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

    def test_interval_item_has_last(self):
        item = (IntervalItemFactory
                .create_item('host1', 'ET_dummyHost:long1',
                                      func='last'))

        self.__test_interval_item(item, range(5), '4')

    def test_interval_item_has_min(self):
        item = (IntervalItemFactory
                .create_item('host1', 'ET_dummyHost:long1',
                                      func='min'))

        self.__test_interval_item(item, range(5), '0')

    def test_interval_item_has_max(self):
        item = (IntervalItemFactory
                .create_item('host1', 'ET_dummyHost:long1',
                                      func='max'))

        self.__test_interval_item(item, range(5), '4')

    def test_interval_item_has_avg(self):
        item = (IntervalItemFactory
                .create_item('host1', 'ET_dummyHost:long1',
                                      func='avg'))

        self.__test_interval_item(item, range(10), '4.5')

    def __test_interval_item(self, item, test_vals, result_value):
        pv = item.pv
        for val in test_vals:
            pv.put(val, wait=True)
        time.sleep(.05)

        metrics = item.get_metrics()
        self.assertEqual(len(metrics), 1)
        self.assertEqual(metrics[0].host, item.host)
        self.assertEqual(metrics[0].key, item.item_key)
        self.assertEqual(metrics[0].value, result_value)

        pv.disconnect()
        metrics = item.get_metrics()
        self.assertEqual(metrics, [])


def main():
    unittest.main(verbosity=2)


if __name__ == '__main__':
    main()
