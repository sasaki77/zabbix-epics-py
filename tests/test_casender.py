#!/usr/bin/env python

import unittest
import os
import time
try:
    import threading
except ImportError:
    import dummy_threading as threading
from epics import ca
from ioccontrol import IocControl
from server import SimpleZabbixServerHandler
from socketserver import TCPServer
from zbxepics.casender import ZabbixSenderCA
from zbxepics.casender import ZabbixSenderItem
from zbxepics.casender import ZabbixSenderItemInterval


class TestZabbixSenderCA(unittest.TestCase):

    def setUp(self):
        ioc_arg_list = ['-m', 'head=ET_dummyHost', '-d', 'test.db']
        self.__iocprocess = IocControl(arg_list=ioc_arg_list)
        self.__iocprocess.start()
        sport = str(IocControl.server_port)
        os.environ['EPICS_CA_AUTO_ADDR_LIST'] = 'NO'
        os.environ['EPICS_CA_ADDR_LIST'] = 'localhost:{}'.format(sport)
        ca.initialize_libca()

    def tearDown(self):
        ca.finalize_libca()
        self.__iocprocess.stop()

    def __start_server(self):
        self._zbx_host = 'localhost'
        self._zbx_port = 30051
        server_address = (self._zbx_host, self._zbx_port)
        handler = SimpleZabbixServerHandler

        TCPServer.allow_reuse_address = True
        self.__zbxserver = TCPServer(server_address, handler)
        th_server = threading.Thread(target=self.__zbxserver.serve_forever)
        th_server.start()

    def __stop_server(self):
        self.__zbxserver.shutdown()

    def test_init(self):
        sender = ZabbixSenderCA('testserver.com', 12345)

        zbx_sender = sender.zbx_sender
        host, port = zbx_sender.zabbix_uri[0]
        self.assertEqual(host, 'testserver.com')
        self.assertEqual(port, 12345)

    def test_add_monitor_item(self):
        item = {'host': 'dummyServerHost',
                'pv': 'ET_dummyHost:ai1',
                'interval': 'monitor'}

        sender = ZabbixSenderCA('testserver.com', 12345)
        mon_item = sender.add_item(item)

        self.assertIsInstance(mon_item, ZabbixSenderItem)
        self.assertEqual(mon_item.host, 'dummyServerHost')
        self.assertEqual(mon_item.pv.pvname, 'ET_dummyHost:ai1')

    def test_add_interval_item(self):
        item = {'host': 'dummyServerHost',
                'pv': 'ET_dummyHost:ai1',
                'interval': 10,
                'func': 'last'}

        sender = ZabbixSenderCA('testserver.com', 12345)
        interval_item = sender.add_item(item)

        self.assertIsInstance(interval_item, ZabbixSenderItemInterval)
        self.assertEqual(interval_item.host, 'dummyServerHost')
        self.assertEqual(interval_item.pv.pvname, 'ET_dummyHost:ai1')
        self.assertEqual(interval_item.interval, 10)

    def test_add_item_err(self):
        item = {'host': 'dummyServerHost',
                'pv': 'ET_dummyHost:ai1'}
        sender = ZabbixSenderCA('testserver.com', 12345)

        with self.assertRaises(KeyError):
            sender.add_item(item)

    def test_run_without_items(self):
        sender = ZabbixSenderCA('testserver.com', 12345)
        with self.assertRaises(Exception):
            sender.run()

    def test_stop_request(self):
        item = {'host': 'dummyServerHost',
                'pv': 'ET_dummyHost:ai',
                'interval': 'monitor'}

        sender = ZabbixSenderCA('testserver.com', 12345)
        sender.add_item(item)

        th_sender = threading.Thread(target=sender.run)
        th_sender.start()

        self.assertTrue(sender.is_running)

        sender.stop()

        self.assertFalse(sender.is_running)

    def _send_metrics(self, metrics=None, result=None):
        self.send_events += result.processed

    def test_sender_ca(self):
        item = {}
        item['host'] = 'dummyServerHost'
        item['pv'] = 'ET_dummyHost:long1'
        item['interval'] = 'monitor'

        self.__start_server()
        self.send_events = 0

        sender = ZabbixSenderCA(self._zbx_host, self._zbx_port,
                                send_callback=self._send_metrics)
        sender_item = sender.add_item(item)
        th_sender = threading.Thread(target=sender.run)
        th_sender.start()

        pv = sender_item.pv
        for i in range(5):
            pv.put(i, wait=True)
        time.sleep(1)

        sender.stop()

        # We get 5 events
        self.assertEqual(self.send_events, 5)

        self.__stop_server()


def main():
    unittest.main(verbosity=2)


if __name__ == '__main__':
    main()
