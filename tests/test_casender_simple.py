#!/usr/bin/env python

import unittest
import os
import time
try:
    import threading
except ImportError:
    import dummy_threading as threading
from epics import caput
from ioccontrol import IocControl
from server import SimpleZabbixServerHandler
from socketserver import TCPServer
from zbxepics.casender import ZabbixSenderCA


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

        self.send_events = 0

    def tearDown(self):
        self.__iocprocess.stop()
        self.__zbxserver.shutdown()

    def __setup_epics_env(self):
        sport = str(self.__iocprocess.server_port)
        os.putenv('EPICS_CA_AUTO_ADDR_LIST', 'NO')
        os.putenv('EPICS_CA_ADDR_LIST', 'localhost:{}'.format(sport))

    def _send_metrics(self, metrics=None, result=None):
        self.send_events += result.processed

    def test_sender_ca(self):
        item = {}
        item['host'] = 'dummyServerHost'
        item['pv'] = 'ET_dummyHost:long1'
        item['interval'] = 'monitor'

        sender = ZabbixSenderCA(self._zbx_host, self._zbx_port,
                                send_callback=self._send_metrics)
        sender.add_item(item)
        th_sender = threading.Thread(target=sender.run)
        th_sender.start()

        for i in range(5):
            caput(item['pv'], i, wait=True)
        time.sleep(1)

        sender.stop()

        # We get 5 events
        self.assertEqual(self.send_events, 5)


def main():
    unittest.main(verbosity=2)


if __name__ == '__main__':
    main()
