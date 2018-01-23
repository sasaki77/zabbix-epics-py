#!/usr/bin/env python

import unittest
import os
import time
from epics import caput
from ioccontrol import IocControl
from zbxepics.casender import ZabbixSenderItemInterval
from zbxepics.casender.peekqueue import PriorityPeekQueue


class TestSenderIntervalItem(unittest.TestCase):

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

    def test_interval_item_metrics(self):
        item = ZabbixSenderItemInterval('host1', 'ET_dummyHost:long1',
                                        10, 'last')

        for val in range(10):
            caput('ET_dummyHost:long1', val, wait=True)

        # Wait until runtime is reached
        runtime = int(time.time()) + item.interval
        while True:
            now = int(time.time())
            if now >= runtime:
                break
            time.sleep(1)

        metrics = item.get_metrics()
        self.assertEqual(len(metrics), 1)

        for zm in metrics:
            self.assertEqual(zm.host, 'host1')
            self.assertEqual(zm.key, 'EPICS[ET_dummyHost:long1]')
            self.assertEqual(zm.value, '9')


def main():
    unittest.main(verbosity=2)


if __name__ == '__main__':
    main()
