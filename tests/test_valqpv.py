#!/usr/bin/env python

import unittest
import os
import time
from epics import ca, caput
from ioccontrol import IocControl
from zbxepics.pvsupport import ValQPV


def setup_epics_env():
    sport = str(IocControl.server_port)
    os.putenv('EPICS_CA_AUTO_ADDR_LIST', 'NO')
    os.putenv('EPICS_CA_ADDR_LIST', 'localhost:{}'.format(sport))


class TestValQPV(unittest.TestCase):

    def __start_ioc(self):
        ioc_arg_list = ['-m', 'head=ET_dummyHost', '-d', 'test.db']
        self.__iocprocess = IocControl(arg_list=ioc_arg_list)
        self.__iocprocess.start()

    def __stop_ioc(self):
        ca.finalize_libca()
        self.__iocprocess.stop()

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

    def test_get_q_all(self):
        self.__start_ioc()

        pv = ValQPV('ET_dummyHost:long1')
        pv.wait_for_connection()

        test_vals = [v for v in range(5)]
        for val in test_vals:
            caput('ET_dummyHost:long1', val, wait=True)
        time.sleep(.05)

        data = pv.get_q_all()
        vals = [v for v, t in data]
        self.assertEqual(vals, test_vals)

        self.__stop_ioc()


def main():
    setup_epics_env()
    unittest.main(verbosity=2)


if __name__ == '__main__':
    main()
