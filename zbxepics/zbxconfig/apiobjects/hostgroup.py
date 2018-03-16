from .apiobject import APIObject
from zbxepics.logging.logger import logger


class HostGroup(APIObject):
    """Host group object class for ZabbixAPI.

    :type host: dict
    :param host: dict for host group object.
        :keys:
            'name': (str)  Name of the host group.
        :optional keys:
            'new_name': (str)  New name of the host group.
    """

    def create(self, groups):
        for group in groups:
            self.create_one(group)

    def create_one(self, group):
        name = group['name']
        groupid = self.get_id_by_name(name)
        if groupid is not None:
            logger.debug('Already exists({0})'.format(name))
            return None

        params = self.__to_parameters(group)

        result = self._do_request('hostgroup.create', params)
        return result['groupids'][0] if result else None

    def update_one(self, group, groupid=None):
        name = group['name']
        if groupid is None:
            groupid = self.get_id_by_name(name)

        if groupid is None:
            logger.debug('Not exists({0})'.format(name))
            return None

        params = self.__to_parameters(group)
        params['groupid'] = groupid
        if 'new_name' in group:
            params['name'] = group['new_name']

        result = self._do_request('hostgroup.update', params)
        return result['groupids'][0] if result else None

    def create_or_update(self, groups):
        for group in groups:
            groupid = self.get_id_by_name(group['name'])
            if groupid is None:
                self.create_one(group)
            else:
                self.update_one(group, groupid)

    def __to_parameters(self, group):
        params = {}
        params['name'] = group['name']

        return params

    def get_hostgroups_by_name(self, names, output=None):
        params = {}
        params['filter'] = {'name': names}
        params['output'] = ['groupid', 'name']
        if output is not None:
            params['output'] = output

        result = self._do_request('hostgroup.get', params)
        return result

    def get_id_by_name(self, name):
        groups = self.get_ids_by_name([name])
        return groups[0]['groupid'] if groups else None

    def get_ids_by_name(self, names):
        groups = self.get_hostgroups_by_name(names, ['groupid'])
        return groups if groups else None

    def delete(self, names):
        groups = self.get_ids_by_name(names)
        if not groups:
            return None

        params = [group['groupid'] for group in groups]

        result = self._do_request('hostgroup.delete', params)
        return result['groupids'] if result else None
