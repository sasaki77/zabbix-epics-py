import json
import copy
import collections

from pyzabbix import ZabbixAPI

from zbxepics.logging.logger import logger
from . import apiobjects


class ZabbixProvisionCA(object):
    """ZabbixProvisionCA class, Provision zabbix configuration."""

    def __init__(self, url=None, user=None, password=None):
        self.__zbx_api = ZabbixAPI(url, user=user, password=password)

        self.__hostgroup = apiobjects.HostGroup(self.__zbx_api)
        self.__host = apiobjects.Host(self.__zbx_api)
        self.__template = apiobjects.Template(self.__zbx_api)
        self.__trigger = apiobjects.Trigger(self.__zbx_api)

    def set_hostgroups(self, hostgroups):
        self.__hostgroup.create_or_update(hostgroups)

    def set_hosts(self, hosts):
        self.__host.create_or_update(hosts)

    def set_templates(self, templates):
        self.__template.create_or_update(templates)

    def set_items(self, items, templated=False):
        itemapi = apiobjects.Item(self.__zbx_api, templated)
        itemapi.create_or_update(items)

    def set_applications(self, applications, templated=False):
        appapi = apiobjects.Application(self.__zbx_api, templated)
        appapi.create_or_update(applications)

    def set_triggers(self, triggers):
        self.__trigger.create_or_update(triggers)

    def exec_provision(self, config):
        """Make provision for zabbix configurations.

        :type config: dict
        :param config: Zabbix configurations. required keys
         'hostgroups', 'hosts', 'templates'
        """
        if config is None:
            return

        if 'hostgroups' in config:
            self.set_hostgroups(config['hostgroups'])

        if 'hosts' in config:
            host_objs = [host['info'] for host in config['hosts']]
            self.set_hosts(host_objs)

            for host_ in config['hosts']:
                self.set_applications(host_['applications'])
                self.set_items(host_['items'])
                self.set_triggers(host_['triggers'])

        if 'templates' in config:
            tpl_objs = [tpl['info'] for tpl in config['templates']]
            self.set_templates(tpl_objs)

            templated = True
            for tpl_ in config['templates']:
                self.set_applications(tpl_['applications'], templated)
                self.set_items(tpl_['items'], templated)
                self.set_triggers(tpl_['triggers'])


class ZabbixProvisionConfigJSON(object):
    """ZabbixProvisionConfigJSON class.

    Load configuration from JSON.
    """

    def __update_nested_dict(self, orig_dict, new_dict):
        for key, val in new_dict.items():
            if isinstance(val, dict):
                tmp = orig_dict.get(key, {})
                orig_dict[key] = self.__update_nested_dict(tmp, val)
            elif isinstance(val, list):
                tmp = orig_dict.get(key, [])
                orig_dict[key] = tmp.extend(val) if tmp else val
            else:
                orig_dict[key] = new_dict[key]
        return orig_dict

    def load_config_from_json(self, config_file):
        """Load zabbix configuration from config file at JSON.

        :type config_file: str
        :param config_file: Path to config file to load
         configurations from.

        :rtype: dict
        :return: Configurations loaded from config file.
        """
        config = {}
        config['hostgroups'] = []
        config['hosts'] = []
        config['templates'] = []

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

            groups = [groupname]
            hosts = group.get('hosts', [])
            for host in hosts:
                host_ = self.__parse_host(host, groups,
                                          default=group_default)
                if host_:
                    config['hosts'].append(host_)

            templates = group.get('templates', [])
            for template in templates:
                template_ = self.__parse_template(template, groups,
                                                  default=group_default)
                if template_:
                    config['templates'].append(template_)

        return config

    def __parse_template(self, template, groups, default=None):
        # Default
        if default is None:
            default = {}
        template_default = copy.deepcopy(default)
        if 'default' in template:
            template_default = self.__update_nested_dict(template_default,
                                                         template['default'])

        template_config = {}
        info = copy.deepcopy(template)
        info['groups'] = groups
        info.pop('default', None)
        info.pop('applications', None)
        info.pop('items', None)
        info.pop('triggers', None)
        template_config['info'] = info

        if 'hosts' in template:
            template_config['info']['hosts'] = template['hosts']

        contents = self.__parse_host_contents(template, template_default)
        if contents:
            template_config['applications'] = contents['applications']
            template_config['items'] = contents['items']
            template_config['triggers'] = contents['triggers']

        return template_config

    def __parse_host(self, host, groups, default=None):
        # Default
        if default is None:
            default = {}
        host_default = copy.deepcopy(default)
        if 'default' in host:
            host_default = self.__update_nested_dict(host_default,
                                                     host['default'])

        host_config = {}
        info = copy.deepcopy(host)
        info['groups'] = groups
        info.pop('default', None)
        info.pop('applications', None)
        info.pop('items', None)
        info.pop('triggers', None)
        host_config['info'] = info

        default_iface = {}
        if 'interface' in host_default:
            default_iface = copy.deepcopy(host_default['interface'])
        if 'interfaces' in host:
            interfaces = []
            for interface in host['interfaces']:
                interface_ = default_iface
                interface_.update(interface)
                interfaces.append(interface_)
            host_config['info']['interfaces'] = interfaces
            if interfaces:
                host_default['item']['interface'] = interfaces[0]

        templates = None
        if 'templates' in host:
            templates = host['templates']
        elif 'templates' in host_default:
            templates = host_default['templates']

        if templates:
            host_config['info']['templates'] = templates

        contents = self.__parse_host_contents(host, host_default)
        if contents:
            host_config['applications'] = contents['applications']
            host_config['items'] = contents['items']
            host_config['triggers'] = contents['triggers']

        return host_config

    def __parse_host_contents(self, host, default=None):
        if default is None:
            default = {}

        contents = {}
        contents['applications'] = []
        contents['items'] = []
        contents['triggers'] = []

        hostname = host['name']
        if 'applications' in host:
            default_item = None
            if 'item' in default:
                default_item = copy.deepcopy(default['item'])
            for app in host['applications']:
                app_name = app['name']
                app_ = {'host': hostname, 'name': app_name}
                contents['applications'].append(app_)
                if 'items' not in app:
                    continue
                items = self.__parse_items(app['items'], hostname,
                                           [app_name], default_item)
                contents['items'].extend(items)

        if 'triggers' in host:
            default_trigger = None
            if 'trigger' in default:
                default_trigger = copy.deepcopy(default['trigger'])
            triggers = self.__parase_triggers(host['triggers'], hostname,
                                              default_trigger)
            contents['triggers'] = triggers

        return contents

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
            if 'dependencies' in trigger_:
                for trg in trigger_['dependencies']:
                    if 'host' not in trg:
                        trg['host'] = hostname
            triggers_.append(trigger_)
        return triggers_
