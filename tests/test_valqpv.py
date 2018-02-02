#!/usr/bin/env python

import unittest
import os
import time

from epics import ca

from ioccontrol import IocControl
from zbxepics.pvsupport import ValQPV


class TestValQPV(unittest.TestCase):

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

    def __on_connect(self, pvname=None, conn=None, chid=None, **kws):
        self.connected = conn

    def testA_init(self):
        pv = ValQPV('ET_dummyHost:ai1')
        self.assertIsNotNone(pv)
        self.assertEqual(pv.pvname, 'ET_dummyHost:ai1')

    def testA_init_with_conn(self):
        self.connected = False
        pv = ValQPV('ET_dummyHost:ai1',
                    connection_callback=self.__on_connect)
        pv.get(use_monitor=False)

        self.assertTrue(self.connected)

    def testA_init_err(self):
        with self.assertRaises(Exception):
            ValQPV()

    def test_get_q_all(self):
        pv = ValQPV('ET_dummyHost:long1')

        test_vals = [v for v in range(5)]
        for val in test_vals:
            pv.put(val, wait=True)
        time.sleep(.05)

        data = pv.get_q_all()
        vals = [v for v, t in data]
        self.assertEqual(vals, test_vals)

        empty_data = pv.get_q_all()
        self.assertEqual(empty_data, [])


def main():
    unittest.main(verbosity=2)


if __name__ == '__main__':
    main()
