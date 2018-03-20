import copy

from .apiobject import APIObject
from .hostgroup import HostGroup
from zbxepics.logging.logger import logger


class Template(APIObject):
    """Template object class for ZabbixAPI.

    :type template: dict
    :param template: dict for template object.
        :keys:
            'name': (str)  Technical name of the template.
            'groups': (array)  Host groups to add the template to.
    """

    def __init__(self, zbx_api):
        self.__hostgroup = HostGroup(zbx_api)
        super(Template, self).__init__(zbx_api)

    def create(self, templates):
        for template in templates:
            self.create_one(template)

    def create_one(self, template):
        """Create new template.

        :type template: dict
        :param template: Paramter of Template object.

        :rtype: str
        :return: Return single ID of the created template.
        """
        name = template['name']
        templateid = self.get_id_by_name(name)
        if templateid is not None:
            logger.debug('Already exists({0})'.format(name))
            return None

        params = self.__to_parameters(template)
        params['groups'] = self.__get_groupids(template['groups'])

        result = self._do_request('template.create', params)
        return result['templateids'][0] if result else None

    def update_one(self, template, templateid=None):
        """Update existing template.

        :type template: dict
        :param template: Paramter of Template object.

        :type templateid: str
        :param templateid: ID of the template.

        :rtype: str
        :return: Return single ID of the updated template.
        """
        name = template['name']
        if templateid is None:
            templateid = self.get_id_by_name(name)

        if templateid is None:
            logger.debug('Not exists({0})'.format(name))
            return None

        params = self.__to_parameters(template)
        params['templateid'] = templateid
        if 'groups' in template:
            params['groups'] = self.__get_groupids(template['groups'])
        if 'templates_clear' in template:
            ids = self.get_ids_by_name(template['templates_clear'])
            params['templates_clear'] = ids

        result = self._do_request('template.update', params)
        return result['templateids'][0] if result else None

    def create_or_update(self, templates):
        for template in templates:
            templateid = self.get_id_by_name(template['name'])
            if templateid is None:
                self.create_one(template)
            else:
                self.update_one(template, templateid)

    def __to_parameters(self, template):
        params = copy.deepcopy(template)
        params['host'] = template['name']
        if 'templates' in params:
            ids = self.get_ids_by_name(params['templates'])
            params['templates'] = ids

        return params

    def get_templates_by_name(self, names, output=None):
        params = {}
        params['filter'] = {'host': names}
        params['output'] = ['templateid', 'host', 'status']
        if output is not None:
            params['output'] = output

        result = self._do_request('template.get', params)
        return result

    def get_id_by_name(self, name):
        templateids = self.get_ids_by_name([name])
        return templateids[0]['templateid'] if templateids else None

    def get_ids_by_name(self, names):
        templates = self.get_templates_by_name(names, ['templateid'])
        return templates if templates else None

    def __get_groupids(self, groups):
        groupids = self.__hostgroup.get_ids_by_name(groups)
        return groupids

    def delete(self, names):
        """Delete templates.

        :type names: list
        :param names: Technical names of the templates to delete.

        :rtype: list
        :return: Return IDs of the deleted templates.
        """
        templates = self.get_ids_by_name(names)
        if not templates:
            return None

        params = [template['templateid'] for template in templates]

        result = self._do_request('template.delete', params)
        return result['templateids'] if result else None
