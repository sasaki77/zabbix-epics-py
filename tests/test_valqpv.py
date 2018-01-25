#!/usr/bin/env python

import unittest
import os
import time
from epics import ca
from ioccontrol import IocControl
from zbxepics.pvsupport import ValQPV


class TestValQPV(unittest.TestCase):

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

    def test_init(self):
        pv = ValQPV('ET_dummyHost:ai1')
        self.assertEqual(pv.pvname, 'ET_dummyHost:ai1')

    def test_init_err(self):
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
