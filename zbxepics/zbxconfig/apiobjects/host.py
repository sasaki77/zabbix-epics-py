from .apiobject import APIObject
from .hostgroup import HostGroup


class Host(APIObject):

    def __init__(self, zbx_api):
        self.__hostgroup = HostGroup(zbx_api)
        super(Host, self).__init__(zbx_api)

    def create(self, hosts):
        for host in hosts:
            self.create_one(host)

    def create_one(self, host):
        name = host['name']
        hostid = self.get_id_by_name(name)
        if hostid is not None:
            raise Exception('Already exists({0})'.format(name))

        params = self.__to_parameters(host)

        result = self._do_request('host.create', params)
        return result['hostids'][0] if result else None

    def update_one(self, host, hostid=None):
        name = host['name']
        if hostid is None:
            hostid = self.get_id_by_name(name)

        if hostid is None:
            raise Exception('Not exists({0})'.format(name))

        params = self.__to_parameters(host)
        params['hostid'] = hostid

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
        params = {}
        params['host'] = host['name']
        params['interfaces'] = host['interfaces']
        params['groups'] = self.__get_hostgroup_ids(host['groups'])

        return params

    def get_hosts_by_name(self, names, output=None):
        params = {}
        params['filter'] = {'host': names}
        params['output'] = ['hostid', 'name', 'interfaces', 'groups']
        if output is not None:
            params['output'] = output

        result = self._do_request('host.get', params)
        return result

    def get_id_by_name(self, name):
        hosts = self.get_hosts_by_name([name])
        return hosts[0]['hostid'] if hosts else None

    def __get_hostgroup_ids(self, groups):
        groupids = (self.__hostgroup
                    .get_hostgroups_by_name(groups, ['groupid']))
        return groupids

    def delete(self, names):
        hosts = self.get_hosts_by_name(names)
        if not hosts:
            return None

        params = [host['hostid'] for host in hosts]

        result = self._do_request('host.delete', params)
        return result['hostids'] if result else None
