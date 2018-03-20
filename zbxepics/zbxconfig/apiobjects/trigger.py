import copy

from .apiobject import APIObject
from zbxepics.logging.logger import logger


class Trigger(APIObject):
    """Trigger object class for ZabbixAPI.

    :type trigger: dict
    :param trigger:
        :keys:
            'description': (str)  Name of the trigger.
            'expression': (str)  Reduced trigger expression.
        :optional keys:
            'priority': (integer)  Severity of the trigger.
            'recovery_expression': (str)  Reduced trigger recovery expression.
            'manual_close': (integer)  Allow manual close.
    """

    def __init__(self, zbx_api):
        super(Trigger, self).__init__(zbx_api)

    def create(self, triggers):
        for trigger in triggers:
            self.create_one(trigger)

    def create_one(self, trigger):
        """Create new trigger.

        :type trigger: dict
        :param trigger: Paramter of Trigger object.

        :rtype: str
        :return: Return single ID of the created trigger.
        """
        triggerid = self.__get_id(trigger)
        if triggerid is not None:
            logger.debug(('Already exists({0})'
                          .format(trigger['expression'])))
            return None

        params = self.__to_parameters(trigger)

        result = self._do_request('trigger.create', params)
        return result['triggerids'][0] if result else None

    def update_one(self, trigger, triggerid=None):
        """Update existing trigger.

        :type trigger: dict
        :param trigger: Paramter of Trigger object.

        :type triggerid: str
        :param triggerid: ID of the trigger.

        :rtype: str
        :return: Return single ID of the updated trigger.
        """
        if triggerid is None:
            triggerid = self.__get_id(trigger)

        if triggerid is None:
            logger.debug(('Not exists({0})'
                          .format(trigger['expression'])))
            return None

        params = self.__to_parameters(trigger)
        params['triggerid'] = triggerid

        result = self._do_request('trigger.update', params)
        return result['triggerids'][0] if result else None

    def create_or_update(self, triggers):
        for trigger in triggers:
            triggerid = self.__get_id(trigger)
            if triggerid is None:
                self.create_one(trigger)
            else:
                self.update_one(trigger, triggerid)

    def __to_parameters(self, trigger):
        params = copy.deepcopy(trigger)
        if 'dependencies' in params:
            ids = self.__get_ids(params['dependencies'])
            params['dependencies'] = ids

        return params

    def get_triggers_by_host(self, hostname, description=None,
                             expand_expression=True, output=None):
        params = {}
        params['filter'] = {'host': hostname, 'description': description}
        params['expandExpression'] = expand_expression
        params['output'] = ['triggerid', 'description', 'expression',
                            'recovery_expression', 'priority',
                            'manual_close']
        if output is not None:
            params['output'] = output

        result = self._do_request('trigger.get', params)
        return result

    def get_id_by_expression(self, expression, hostname,
                             description=None):
        triggers = self.get_triggers_by_host(hostname, description)
        if not triggers:
            return None

        triggerid = None
        for trigger in triggers:
            if trigger['expression'] == expression:
                triggerid = trigger['triggerid']
                break

        return triggerid

    def __get_id(self, trigger):
        triggerid = self.get_id_by_expression(trigger['expression'],
                                              trigger['host'],
                                              trigger['description'])
        return triggerid

    def __get_ids(self, triggers):
        triggerids = []
        for trigger in triggers:
            id_ = self.get_id_by_expression(trigger['expression'],
                                            trigger['host'],
                                            trigger['description'])
            if id_:
                triggerids.append({'triggerid': id_})

        return triggerids

    def delete(self, hostname, expressions):
        """Delete triggers.

        :type hostname: str
        :param hostname: Technical name of the host.

        :type expressions: str or list
        :param expressions: Expressions of the triggers to delete.

        :rtype: list
        :return: Return IDs of the deleted triggers.
        """
        triggers = self.get_triggers_by_host(hostname)
        if not triggers:
            return None

        if not isinstance(expressions, (tuple, list)):
            expressions = [expressions]
        params = []
        for trigger in triggers:
            if trigger['expression'] in expressions:
                params.append(trigger['triggerid'])

        result = self._do_request('trigger.delete', params)
        return result['triggerids'] if result else None
