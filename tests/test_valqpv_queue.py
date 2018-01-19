#!/usr/bin/env python

import unittest
import os
import time
from epics import caput
from ioccontrol import IocControl
from zbxepics.pvsupport import ValQPV


class TestQueue(unittest.TestCase):

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

    def test_get_q_all(self):
        pv = ValQPV('ET_dummyHost:long1')
        pv.wait_for_connection()

        test_vals = [v for v in range(5)]
        for val in test_vals:
            caput('ET_dummyHost:long1', val, wait=True)
        time.sleep(.05)

        data = pv.get_q_all()
        vals = [v for v, t in data]
        self.assertEqual(vals, test_vals)


def main():
    unittest.main(verbosity=2)


if __name__ == '__main__':
    main()
