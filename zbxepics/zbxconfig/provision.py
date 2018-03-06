import json
import copy
import collections

from pyzabbix import ZabbixAPI

from zbxepics.logging.logger import logger
from . import apiobjects


class ZabbixProvisionCA(object):

    def __init__(self, url=None, user=None, password=None):
        self.__zbx_api = ZabbixAPI(url, user=user, password=password)

        self.__hostgroup = apiobjects.HostGroup(self.__zbx_api)
        self.__host = apiobjects.Host(self.__zbx_api)
        self.__item = apiobjects.Item(self.__zbx_api)
        self.__application = apiobjects.Application(self.__zbx_api)
        self.__trigger = apiobjects.Trigger(self.__zbx_api)

    def set_hostgroups(self, hostgroups):
        self.__hostgroup.create_or_update(hostgroups)

    def set_hosts(self, hosts):
        self.__host.create_or_update(hosts)

    def set_items(self, items):
        self.__item.create_or_update(items)

    def set_applications(self, applications):
        self.__application.create_or_update(applications)

    def set_triggers(self, triggers):
        self.__trigger.create_or_update(triggers)

    def exec_provision(self, config):
        if config is None:
            return

        if 'hostgroups' in config:
            self.set_hostgroups(config['hostgroups'])
        if 'hosts' in config:
            self.set_hosts(config['hosts'])
        if 'applications' in config:
            self.set_applications(config['applications'])
        if 'items' in config:
            self.set_items(config['items'])
        if 'triggers' in config:
            self.set_triggers(config['triggers'])


class ZabbixProvisionConfigJSON(object):

    def __update_nested_dict(self, orig_dict, new_dict):
        for key, val in new_dict.items():
            if isinstance(val, dict):
                tmp = orig_dict.get(key, {})
                orig_dict[key] = self.__update_nested_dict(tmp, val)
            elif isinstance(val, list):
                orig_dict[key] = orig_dict.get(key, []).extend(val)
            else:
                orig_dict[key] = new_dict[key]
        return orig_dict

    def load_config_from_json(self, config_file):
        config = {}
        config['hostgroups'] = []
        config['hosts'] = []
        config['applications'] = []
        config['items'] = []
        config['triggers'] = []

        with open(config_file, 'r') as f:
            json_data = json.load(f)

        # Read default configuration
        top_default = {}
        if 'default' in json_data:
            top_default = json_data['default']

        # Read configuration
        if 'hostgroups' not in json_data:
            return config

        for group in json_data['hostgroups']:
            # Default in group
            group_default = copy.deepcopy(top_default)
            if 'default' in group:
                group_default = self.__update_nested_dict(group_default,
                                                          group['default'])
            groupname = group['name']
            group_ = {'name': groupname}
            config['hostgroups'].append(group_)

            if 'hosts' not in group:
                continue
            for host in group['hosts']:
                host_ = self.__parse_host(host, [groupname],
                                          group_default)
                if host_:
                    config['hosts'].append(host_['host'])
                    config['applications'].extend(host_['applications'])
                    config['items'].extend(host_['items'])
                    config['triggers'].extend(host_['triggers'])

        return config

    def __parse_host(self, host, groups, default=None):
        # Default
        if default is None:
            default = {}
        host_default = copy.deepcopy(default)
        if 'default' in host:
            host_default = self.__update_nested_dict(host_default,
                                                     host['default'])

        hostname = host['name']
        host_config = {}
        host_config['host'] = {'name': hostname, 'groups': groups}
        host_config['applications'] = []
        host_config['items'] = []
        host_config['triggers'] = []

        default_iface = {}
        if 'interface' in host_default:
            default_iface = copy.deepcopy(host_default['interface'])
        if 'interfaces' in host:
            interfaces = []
            for interface in host['interfaces']:
                interface_ = default_iface
                interface_.update(interface)
                interfaces.append(interface_)
            host_config['host']['interfaces'] = interfaces
            if interfaces:
                host_default['item']['interface'] = interfaces[0]

        if 'applications' in host:
            default_item = None
            if 'item' in host_default:
                default_item = copy.deepcopy(host_default['item'])
            for app in host['applications']:
                app_name = app['name']
                app_ = {'host': hostname, 'name': app_name}
                host_config['applications'].append(app_)
                if 'items' not in app:
                    continue
                items = self.__parse_items(app['items'], hostname,
                                           [app_name], default_item)
                host_config['items'].extend(items)

        if 'triggers' in host:
            default_trigger = None
            if 'trigger' in host_default:
                default_trigger = copy.deepcopy(host_default['trigger'])
            triggers = self.__parase_triggers(host['triggers'], hostname,
                                              default_trigger)
            host_config['triggers'] = triggers

        return host_config

    def __parse_items(self, items, hostname, apps, default=None):
        if default is None:
            default = {}
        items_ = []
        for item in items:
            item_ = copy.deepcopy(default)
            item_.update(item)
            item_['host'] = hostname
            item_['applications'] = apps
            items_.append(item_)
        return items_

    def __parase_triggers(self, triggers, hostname, default=None):
        if default is None:
            default = {}
        triggers_ = []
        for trigger in triggers:
            trigger_ = copy.deepcopy(default)
            trigger_.update(trigger)
            trigger_['host'] = hostname
            triggers_.append(trigger_)
        return triggers_
