#!/usr/bin/env python

import unittest
import os
import time
try:
    import threading
except ImportError:
    import dummy_threading as threading
from ioccontrol import IocControl
from server import SimpleZabbixServerHandler
from socketserver import TCPServer
from zbxepics.casender import ZabbixSenderCA
from zbxepics.pvsupport import ValQPV


class TestZabbixSenderCA(unittest.TestCase):

    def setUp(self):
        ioc_arg_list = ['-m', 'head=ET_dummyHost', '-d', 'test.db']
        self.__iocprocess = IocControl(arg_list=ioc_arg_list)
        self.__iocprocess.start()
        self.__setup_epics_env()

        self._zbx_host = 'localhost'
        self._zbx_port = 30051
        server_address = (self._zbx_host, self._zbx_port)
        handler = SimpleZabbixServerHandler

        self.__zbxserver = TCPServer(server_address, handler)
        th_server = threading.Thread(target=self.__zbxserver.serve_forever)
        th_server.start()

        self.__items = self.__create_items()
        self.__sender = ZabbixSenderCA(self._zbx_host, self._zbx_port,
                                       items=self.__items)
        th_sender = threading.Thread(target=self.__sender.run)
        th_sender.start()

    def tearDown(self):
        self.__iocprocess.stop()
        self.__zbxserver.shutdown()

    def __setup_epics_env(self):
        sport = str(self.__iocprocess.server_port)
        os.putenv('EPICS_CA_AUTO_ADDR_LIST', 'NO')
        os.putenv('EPICS_CA_ADDR_LIST', 'localhost:{}'.format(sport))

    def __create_items(self):
        item = {}
        item['host'] = 'dummyServerHost'
        item['pv'] = ValQPV('ioc:countup')
        item['interval'] = 'monitor'

        return (item,)

    def test_sender_ca(self):
        pv = self.__items[0]['pv']
        for i in range(5):
            pv.put(i, wait=True)
            time.sleep(1)

        self.__sender.stop()
        send_total = self.__sender.total

        # We get 5 events: at connection, then at 5 value changes (puts)
        self.assertTrue(send_total == 5,
                        'Send total: %d/5'.format(send_total))


def main():
    unittest.main(verbosity=2)


if __name__ == '__main__':
    main()
