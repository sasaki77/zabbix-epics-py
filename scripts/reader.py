import copy
import json

from zbxepics.logging import logger


class ZabbixConfigReader(object):
    """ZabbixConfigReader class, load configuration from file."""

    def __init__(self):
        self._items = []

    def get_items(self):
        return self._items

    def _add_item(self, hostname, pvname, interval, func=None, item_key=None):
        if (not bool(hostname)
                or not bool(pvname)):
            logger.error('hostname or pvname is undifined.')
            return

        item = {}
        item['host'] = hostname
        item['pv'] = pvname
        item['interval'] = interval
        if func:
            item['func'] = func
        item['item_key'] = item_key

        self._items.append(item)

    # Override these methods to implement other reader.
    def read_config(self, config_file):
        """
        Read configuration from config_file.

        May be overridden by a subclass.
        """
        pass


class ZabbixConfigReaderJSON(ZabbixConfigReader):
    """ZabbixConfigReaderJSON class.

    Load configuration from JSON file.
    """

    def __init__(self, config_file):
        super(ZabbixConfigReaderJSON, self).__init__()

        self.read_config(config_file)

    def read_config(self, config_file):
        self._items = []
        with open(config_file, 'r') as f:
            json_data = json.load(f)

        # Read default configuration
        default_host = {}
        default_item = {}
        if 'default' in json_data:
            if 'host' in json_data['default']:
                default_host = json_data['default']['host']
            if 'item' in default_host:
                default_item = default_host['item']

        # Read configuration
        for host_ in json_data['hosts']:
            host = copy.deepcopy(default_host)
            host.update(host_)
            if host['items'] is None:
                continue

            default_item_ = copy.deepcopy(default_item)
            if 'default' in host:
                if 'item' in host['default']:
                    default_item_.update(host['default']['item'])

            for item_ in host['items']:
                item = copy.deepcopy(default_item_)
                item.update(item_)
                func = None
                if 'func' in item:
                    func = item['func']
                item_key = None
                if 'item_key' in item:
                    item_key = item['item_key']

                self._add_item(host['name'], item['pv'],
                               item['update'], func, item_key)
