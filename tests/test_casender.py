#!/usr/bin/env python

import unittest
try:
    import threading
except ImportError:
    import dummy_threading as threading
from zbxepics.casender import ZabbixSenderCA
from zbxepics.casender import ZabbixSenderItem
from zbxepics.casender import ZabbixSenderItemInterval


class TestZabbixSenderCAInit(unittest.TestCase):

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


def main():
    unittest.main(verbosity=2)


if __name__ == '__main__':
    main()
