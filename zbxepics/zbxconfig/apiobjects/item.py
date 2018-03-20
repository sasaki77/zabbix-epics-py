import copy

from .apiobject import APIObject
from .host import Host
from .template import Template
from .application import Application
from .hostinterface import HostInterface
from zbxepics.logging.logger import logger


class Item(APIObject):
    """Item object class for ZabbixAPI.

    :type item: dict
    :param item:
        :keys:
            'key_': (string)  Item key.
            'name': (string)  Name of the item.
            'type': (integer)  Type of the item.
            'value_type': (integer)  Type of information of the item.
            'host':  (string)  Name of the host that the item belongs to.
        :other keys:
            See also `API` in Zabbix Documentation.
    """

    def __init__(self, zbx_api, templated=False):
        if templated:
            self.__host = Template(zbx_api)
        else:
            self.__host = Host(zbx_api)
        self.__app = Application(zbx_api, templated)
        self.__iface = HostInterface(zbx_api)
        super(Item, self).__init__(zbx_api)

    def create(self, items):
        for item in items:
            self.create_one(item)

    def create_one(self, item):
        """Create new item.

        :type item: dict
        :param item: Paramter of Item object.

        :rtype: str
        :return: Return single ID of the created item.
        """
        key_ = item['key_']
        hostname = item['host']
        itemid = self.get_id_by_key(key_, hostname)
        if itemid is not None:
            logger.debug(('Already exists({0}:{1})'
                          .format(hostname, key_)))
            return None

        params = self.__to_parameters(item)
        params['hostid'] = self.__host.get_id_by_name(hostname)

        result = self._do_request('item.create', params)
        return result['itemids'][0] if result else None

    def update_one(self, item, itemid=None):
        """Update existing item.

        :type item: dict
        :param item: Paramter of Item object.

        :type itemid: str
        :param itemid: ID of the item.

        :rtype: str
        :return: Return single ID of the updated item.
        """
        key_ = item['key_']
        hostname = item['host']
        if itemid is None:
            itemid = self.get_id_by_key(key_, hostname)

        if itemid is None:
            logger.debug(('Not exists({0}:{1})'
                          .format(hostname, key_)))
            return None

        params = self.__to_parameters(item)
        params['itemid'] = itemid

        result = self._do_request('item.update', params)
        return result['itemids'][0] if result else None

    def __to_parameters(self, item):
        params = copy.deepcopy(item)
        if 'interface' in params:
            iface = params['interface']
            ifaceid = self.__iface.get_id_by_ip(params['host'], iface['ip'],
                                                iface['port'])
            params['interfaceid'] = ifaceid
            params.pop('interface', None)
        if 'applications' in params:
            app_names = params['applications']
            app_ids = self.__get_app_ids(app_names, params['host'])
            params['applications'] = app_ids

        return params

    def create_or_update(self, items):
        for item in items:
            itemid = self.get_id_by_key(item['key_'], item['host'])
            if itemid is None:
                self.create_one(item)
            else:
                self.update_one(item, itemid)

    def get_items_by_key(self, keys, hostname=None, output=None):
        params = {}
        params['filter'] = {'key_': keys, 'host': hostname}
        params['output'] = ['itemid', 'name', 'key_']
        if output is not None:
            params['output'] = output

        result = self._do_request('item.get', params)
        return result

    def get_id_by_key(self, key_, hostname):
        items = self.get_items_by_key([key_], hostname)
        return items[0]['itemid'] if items else None

    def __get_app_ids(self, app_names, hostname):
        apps = self.__app.get_ids_by_name(app_names, hostname)
        if not apps:
            return None

        app_ids = [app['applicationid'] for app in apps]
        return app_ids

    def delete(self, hostname, keys):
        """Delete items.

        :type hostname: str
        :param hostname: Technical name of the host.

        :type keys: list
        :param keys: Keys of the items to delete.

        :rtype: list
        :return: Return IDs of the deleted items.
        """
        items = self.get_items_by_key(keys, hostname)
        if not items:
            return None

        params = [item['itemid'] for item in items]

        result = self._do_request('item.delete', params)
        return result['itemids'] if result else None
