import copy

from .apiobject import APIObject
from .hostgroup import HostGroup
from .template import Template
from zbxepics.logging.logger import logger


class Host(APIObject):
    """Host object class for ZabbixAPI.

    :type host: dict
    :param host: dict for host object.
        :keys:
            'name': (str)  Technical name of the host.
            'interfaces': (array)  Interfaces to be created for the host.
            'groups': (array)  Host groups to add the host to.
    """

    def __init__(self, zbx_api):
        self.__hostgroup = HostGroup(zbx_api)
        self.__template = Template(zbx_api)
        super(Host, self).__init__(zbx_api)

    def create(self, hosts):
        for host in hosts:
            self.create_one(host)

    def create_one(self, host):
        """Create new host.

        :type host: dict
        :param host: Paramter of Host object.

        :rtype: str
        :return: Return single ID of the created host.
        """
        name = host['name']
        hostid = self.get_id_by_name(name)
        if hostid is not None:
            logger.debug('Already exists({0})'.format(name))
            return None

        params = self.__to_parameters(host)

        result = self._do_request('host.create', params)
        return result['hostids'][0] if result else None

    def update_one(self, host, hostid=None):
        """Update existing host.

        :type host: dict
        :param host: Paramter of Host object.

        :type hostid: str
        :param hostid: ID of the host.

        :rtype: str
        :return: Return single ID of the updated host.
        """
        name = host['name']
        if hostid is None:
            hostid = self.get_id_by_name(name)

        if hostid is None:
            logger.debug('Not exists({0})'.format(name))
            return None

        params = self.__to_parameters(host)
        params['hostid'] = hostid
        if 'templates_clear' in host:
            templateids = self.__get_templateids(host['templates_clear'])
            params['templates_clear'] = templateids

        result = self._do_request('host.update', params)
        return result['hostids'][0] if result else None

    def create_or_update(self, hosts):
        for host in hosts:
            hostid = self.get_id_by_name(host['name'])
            if hostid is None:
                self.create_one(host)
            else:
                self.update_one(host, hostid)

    def __to_parameters(self, host):
        params = copy.deepcopy(host)
        params['host'] = host['name']
        params['groups'] = self.__get_groupids(host['groups'])
        if 'templates' in params:
            templateids = self.__get_templateids(params['templates'])
            params['templates'] = templateids

        return params

    def get_hosts_by_name(self, names, output=None):
        params = {}
        params['filter'] = {'host': names}
        params['output'] = ['hostid', 'host', 'name']
        if output is not None:
            params['output'] = output

        result = self._do_request('host.get', params)
        return result

    def get_id_by_name(self, name):
        hostids = self.get_ids_by_name([name])
        return hostids[0]['hostid'] if hostids else None

    def get_ids_by_name(self, names):
        hosts = self.get_hosts_by_name(names, ['hostid'])
        return hosts if hosts else None

    def __get_groupids(self, groups):
        groupids = self.__hostgroup.get_ids_by_name(groups)
        return groupids

    def __get_templateids(self, templates):
        templateids = self.__template.get_ids_by_name(templates)
        return templateids

    def delete(self, names):
        """Delete hosts.

        :type names: list
        :param names: Technical names of the hosts to delete.

        :rtype: list
        :return: Return IDs of the deleted hosts.
        """
        hosts = self.get_ids_by_name(names)
        if not hosts:
            return None

        params = [host['hostid'] for host in hosts]

        result = self._do_request('host.delete', params)
        return result['hostids'] if result else None
