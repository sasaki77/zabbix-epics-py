#!/usr/bin/env python

import unittest
import os
from http.server import HTTPServer
try:
    import threading
except ImportError:
    import dummy_threading as threading

from pyzabbix import ZabbixAPI

import zbxepics.zbxconfig.apiobjects as apiobjects
from httpserver import ZabbixHTTPRequestHandler


class TestAPIObjects(unittest.TestCase):

    def setUp(self):
        host = 'localhost'
        port = 30051
        handler = ZabbixHTTPRequestHandler
        HTTPServer.allow_reuse_address = True
        self.__httpd = HTTPServer((host, port), handler)
        thread_target = self.__httpd.serve_forever
        self.__th_server = threading.Thread(target=thread_target)
        self.__th_server.daemon = True
        self.__th_server.start()

        address = ':'.join([host, str(port)])
        self._zbx_api = ZabbixAPI(url='http://{0}'.format(address))
        # self._zbx_api = ZabbixAPI()

    def tearDown(self):
        self.__httpd.shutdown()
        self.__th_server.join()
        self.__httpd.server_close()

    def testA_init_hostgroup(self):
        hostgroup = apiobjects.HostGroup(self._zbx_api)
        self.assertIsNotNone(hostgroup)

    def test_hostgroup_create(self):
        hostgroup = apiobjects.HostGroup(self._zbx_api)

        params = {'name': 'Dummy Hosts'}
        groupid = hostgroup.create_one(params)
        self.assertIsNone(groupid)

    def test_hostgroup_update(self):
        hostgroup = apiobjects.HostGroup(self._zbx_api)

        params = {'name': 'Dummy Hosts'}
        groupid = hostgroup.update_one(params)
        self.assertIsNotNone(groupid)

    def testA_init_host(self):
        host = apiobjects.Host(self._zbx_api)
        self.assertIsNotNone(host)

    def test_host_create(self):
        host = apiobjects.Host(self._zbx_api)

        interface = {'type': 1, 'main': 1, 'useip': 1,
                     'ip': '192.168.1.10', 'dns': '', 'port': '10050'}
        params = {'name': 'dummyServerHost',
                  'interfaces': [interface],
                  'groups': ['Dummy Group']}
        hostid = host.create_one(params)
        self.assertIsNone(hostid)

    def test_host_update(self):
        host = apiobjects.Host(self._zbx_api)

        interface = {'type': 1, 'main': 1, 'useip': 0,
                     'ip': '192.168.1.10', 'dns': 'dummyServerHost',
                     'port': '10050'}
        params = {'name': 'dummyServerHost',
                  'interfaces': [interface],
                  'groups': ['Dummy Group']}
        hostid = host.update_one(params)
        self.assertIsNotNone(hostid)

    def testA_init_item(self):
        item = apiobjects.Item(self._zbx_api)
        self.assertIsNotNone(item)

    def test_item_create(self):
        item = apiobjects.Item(self._zbx_api)

        params = {'host': 'dummyServerHost',
                  'name': 'Dummy Item',
                  'key_': 'dummy.key',
                  'type': 2,
                  'value_type': 0,
                  'trapper_hosts': ''}
        itemid = item.create_one(params)
        self.assertIsNone(itemid)

    def test_item_update(self):
        item = apiobjects.Item(self._zbx_api)

        params = {'host': 'dummyServerHost',
                  'name': 'Dummy Item',
                  'key_': 'dummy.key',
                  'type': 2,
                  'value_type': 0,
                  'trapper_hosts': '',
                  'applications': ['Dummy Status']}
        itemid = item.update_one(params)
        self.assertIsNotNone(itemid)

    def testA_init_application(self):
        app = apiobjects.Application(self._zbx_api)
        self.assertIsNotNone(app)

    def test_application_create(self):
        app = apiobjects.Application(self._zbx_api)

        params = {'name': 'Dummy Status',
                  'host': 'dummyServerHost'}
        appid = app.create_one(params)
        self.assertIsNone(appid)

    def test_application_update(self):
        app = apiobjects.Application(self._zbx_api)

        params = {'name': 'Dummy Status',
                  'host': 'dummyServerHost',
                  'new_name': 'Dummy Status2'}
        appid = app.update_one(params)
        self.assertIsNotNone(appid)

    def testA_init_trigger(self):
        trigger = apiobjects.Trigger(self._zbx_api)
        self.assertIsNotNone(trigger)

    def test_trigger_create(self):
        trigger = apiobjects.Trigger(self._zbx_api)

        params = {'host': 'dummyServerHost',
                  'description': 'Dummy Trigger',
                  'expression': '{dummyServerHost:dummy.key.last()}>0',
                  'severity': '3',
                  'recovery_expression': '',
                  'manual_close': '0'}
        triggerid = trigger.create_one(params)
        self.assertIsNone(triggerid)

    def test_trigger_update(self):
        trigger = apiobjects.Trigger(self._zbx_api)

        params = {'host': 'dummyServerHost',
                  'description': 'Dummy Trigger',
                  'expression': '{dummyServerHost:dummy.key.last()}>0',
                  'severity': '1',
                  'recovery_expression': '',
                  'manual_close': '0'}
        triggerid = trigger.update_one(params)
        self.assertIsNotNone(triggerid)

    def testA_init_template(self):
        template = apiobjects.Template(self._zbx_api)
        self.assertIsNotNone(template)

    def test_template_create(self):
        template = apiobjects.Template(self._zbx_api)

        params = {'name': 'Template dummy',
                  'groups': ['Template/Dummy']}
        templateid = template.create_one(params)
        self.assertIsNone(templateid)

    def test_template_update(self):
        template = apiobjects.Template(self._zbx_api)

        params = {'name': 'Template dummy',
                  'groups': ['Template/Dummy'],
                  'hosts': ['dummyServerHost']}
        templateid = template.update_one(params)
        self.assertIsNotNone(templateid)


def main():
    unittest.main(verbosity=2)


if __name__ == '__main__':
    main()
