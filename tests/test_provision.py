#!/usr/bin/env python

import unittest
import os
from http.server import HTTPServer
try:
    import threading
except ImportError:
    import dummy_threading as threading

import zbxepics.zbxconfig.provision as provision
from httpserver import ZabbixHTTPRequestHandler


class TestZabbixProvisionCA(unittest.TestCase):

    def setUp(self):
        self.__server_address = ('localhost', 30051)
        handler = ZabbixHTTPRequestHandler

        HTTPServer.allow_reuse_address = True
        self.__httpd = HTTPServer(self.__server_address, handler)
        thread_target = self.__httpd.serve_forever
        self.__th_server = threading.Thread(target=thread_target)
        self.__th_server.daemon = True
        self.__th_server.start()

    def tearDown(self):
        self.__httpd.shutdown()
        self.__th_server.join()
        self.__httpd.server_close()
        pass

    def test_load_config(self):
        dir_path = os.path.dirname(__file__)
        config_file = os.path.join(dir_path, 'test_zbxconfig.json')
        loader = provision.ZabbixProvisionConfigJSON()
        config_data = loader.load_config_from_json(config_file)
        self.assertIsNotNone(config_data)
        fileds = ['hostgroups', 'hosts', 'templates']
        self.assertEqual(sorted(config_data.keys()), sorted(fileds))

        # url = 'http://localhost/zabbix'
        # provisioner = provision.ZabbixProvisionCA(url=url, user='report',
        #                                           password='report')
        # provisioner.exec_provision(config_data)

    def testA_init(self):
        host, port = self.__server_address
        url = 'http://{host}:{port}'.format(host=host, port=port)
        provisioner = provision.ZabbixProvisionCA(url=url)
        self.assertIsNotNone(provisioner)

    def test_set_hostgroups(self):
        host, port = self.__server_address
        url = 'http://{host}:{port}'.format(host=host, port=port)
        provisioner = provision.ZabbixProvisionCA(url=url)

        params = [{'name': 'Dummy Group'}]
        provisioner.set_hostgroups(params)


def main():
    unittest.main(verbosity=2)


if __name__ == '__main__':
    main()
