#!/usr/bin/env python

import unittest
import os
from epics import caput
from ioccontrol import IocControl
from zbxepics.casender import ZabbixSenderItem


class TestSenderMonitorItem(unittest.TestCase):

    def setUp(self):
        ioc_arg_list = ['-m', 'head=ET_dummyHost', '-d', 'test.db']
        self.__iocprocess = IocControl(arg_list=ioc_arg_list)
        self.__iocprocess.start()
        self.__setup_epics_env()

    def tearDown(self):
        self.__iocprocess.stop()

    def __setup_epics_env(self):
        sport = str(self.__iocprocess.server_port)
        os.putenv('EPICS_CA_AUTO_ADDR_LIST', 'NO')
        os.putenv('EPICS_CA_ADDR_LIST', 'localhost:{}'.format(sport))

    def test_monitor_item_metrics(self):
        item = ZabbixSenderItem('host1', 'ET_dummyHost:long1', 'monitor')

        test_vals = [v for v in range(10)]
        for val in test_vals:
            caput('ET_dummyHost:long1', val, wait=True)

        metrics = item.get_metrics()
        self.assertEqual(len(metrics), 10)

        for (zm, tval) in zip(metrics, test_vals):
            self.assertEqual(zm.host, 'host1')
            self.assertEqual(zm.key, 'EPICS[ET_dummyHost:long1]')
            self.assertEqual(zm.value, str(tval))


def main():
    unittest.main(verbosity=2)


if __name__ == '__main__':
    main()
