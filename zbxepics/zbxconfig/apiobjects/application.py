from .apiobject import APIObject
from .host import Host
from .template import Template
from zbxepics.logging.logger import logger


class Application(APIObject):
    """Application object class for ZabbixAPI.

    :type application: dict
    :param application: dict for application object.
        :keys:
            'name': (str)  Name of the application.
            'host': (str)  Name of the host that the item belongs to.
    """

    def __init__(self, zbx_api, templated=False):
        if templated:
            self.__host = Template(zbx_api)
        else:
            self.__host = Host(zbx_api)
        super(Application, self).__init__(zbx_api)

    def create(self, applications):
        for application in applications:
            self.create_one(application)

    def create_one(self, application):
        """Create new application.

        :type application: dict
        :param application: Paramter of Application object.

        :rtype: str
        :return: Return single ID of the created application.
        """
        name = application['name']
        hostname = application['host']
        applicationid = self.get_id_by_name(name, hostname)
        if applicationid is not None:
            logger.debug('Already exists({0},{1})'.format(hostname, name))
            return None

        params = self.__to_parameters(application)
        params['hostid'] = self.__host.get_id_by_name(hostname)

        result = self._do_request('application.create', params)
        return result['applicationids'][0] if result else None

    def update_one(self, application, applicationid=None):
        """Update existing application.

        :type application: dict
        :param application: Paramter of Application object.

        :type applicationid: str
        :param applicationid: ID of the application.

        :rtype: str
        :return: Return single ID of the updated application.
        """
        name = application['name']
        hostname = application['host']
        if applicationid is None:
            applicationid = self.get_id_by_name(name, hostname)

        if applicationid is None:
            logger.debug('Not exists({0},{1})'.format(hostname, name))
            return None

        params = self.__to_parameters(application)
        params['applicationid'] = applicationid

        result = self._do_request('application.update', params)
        return result['applicationids'][0] if result else None

    def create_or_update(self, applications):
        for application in applications:
            appid = self.get_id_by_name(application['name'],
                                        application['host'])
            if appid is None:
                self.create_one(application)
            else:
                self.update_one(application, appid)

    def __to_parameters(self, application):
        params = {}
        params['name'] = application['name']

        return params

    def get_applications_by_name(self, names, hostname=None, output=None):
        hostid = self.__host.get_id_by_name(hostname)
        params = {}
        params['filter'] = {'hostid': hostid, 'name': names}
        params['output'] = ['applicationid', 'hostid', 'name']
        if output is not None:
            params['output'] = output

        result = self._do_request('application.get', params)
        return result

    def get_id_by_name(self, name, hostname):
        apps = self.get_ids_by_name([name], hostname)
        return apps[0]['applicationid'] if apps else None

    def get_ids_by_name(self, names, hostname):
        apps = self.get_applications_by_name(names, hostname,
                                             ['applicationid'])
        return apps if apps else None

    def delete(self, names, hostname):
        """Delete applications.

        :type names: list
        :param names: Names of the applications to delete.

        :type hostname: str
        :param hostname: Technical name of the host.

        :rtype: list
        :return: Return IDs of the deleted applications.
        """
        apps = self.get_ids_by_name(names, hostname)
        if not apps:
            return None

        params = [app['applicationid'] for app in apps]

        result = self._do_request('application.delete', params)
        return result['applicationids'] if result else None
