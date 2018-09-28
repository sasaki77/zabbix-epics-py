#!/usr/bin/env python

import unittest
import os
import time
try:
    import threading
except ImportError:
    import dummy_threading as threading
from socketserver import TCPServer

from epics import ca

import zbxstreamserver
from ioccontrol import IocControl
from zbxepics.casender import ZabbixSenderCA
from zbxepics.casender.item.monitoritem import MonitorItem
from zbxepics.casender.item.intervalitem import IntervalItem


class TestZabbixSenderCA(unittest.TestCase):

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

    def __start_server(self):
        self._zbx_host = 'localhost'
        self._zbx_port = 30051
        server_address = (self._zbx_host, self._zbx_port)
        handler = zbxstreamserver.SimpleZabbixServerHandler

        TCPServer.allow_reuse_address = True
        self.__zbxserver = TCPServer(server_address, handler)
        thread_target = self.__zbxserver.serve_forever
        self.__th_server = threading.Thread(target=thread_target)
        self.__th_server.daemon = True
        self.__th_server.start()

    def __stop_server(self):
        self.__zbxserver.shutdown()
        self.__th_server.join()
        self.__zbxserver.server_close()

    def testA_init(self):
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
        sender_item = sender.add_item(item)

        self.assertIsNotNone(sender_item)
        self.assertIsInstance(sender_item, MonitorItem)

    def test_add_interval_item(self):
        item = {'host': 'dummyServerHost',
                'pv': 'ET_dummyHost:ai1',
                'interval': 10,
                'func': 'last'}

        sender = ZabbixSenderCA('testserver.com', 12345)
        sender_item = sender.add_item(item)

        self.assertIsNotNone(sender_item)
        self.assertIsInstance(sender_item, IntervalItem)

    def test_add_item_err(self):
        item = {'host': 'dummyServerHost',
                'pv': 'ET_dummyHost:ai1'}
        sender = ZabbixSenderCA('testserver.com', 12345)
        sender_item = sender.add_item(item)

        self.assertIsNone(sender_item)

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
        th_sender.daemon = True
        th_sender.start()

        time.sleep(1)
        self.assertTrue(sender.is_running)
        sender.stop()
        self.assertFalse(sender.is_running)

        th_sender.join()

    def test_sender_ca(self):
        item = {'host': 'dummyServerHost',
                'pv': 'ET_dummyHost:long1',
                'interval': 'monitor'}

        self.__start_server()

        sender = ZabbixSenderCA(self._zbx_host, self._zbx_port)
        sender_item = sender.add_item(item)
        th_sender = threading.Thread(target=sender.run)
        th_sender.daemon = True
        th_sender.start()

        pv = sender_item.pv
        for i in range(5):
            pv.put(i, wait=True)
        time.sleep(1)

        sender.stop()
        th_sender.join()

        self.assertEqual(zbxstreamserver.metrics_received, 5)

        self.__stop_server()


def main():
    unittest.main(verbosity=2)


if __name__ == '__main__':
    main()
