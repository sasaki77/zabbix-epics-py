from .apiobject import APIObject


class Trigger(APIObject):

    def __init__(self, zbx_api):
        super(Trigger, self).__init__(zbx_api)

    def create(self, triggers):
        for trigger in triggers:
            self.create_one(trigger)

    def create_one(self, trigger):
        triggerid = self.__get_id(trigger)
        if triggerid is not None:
            msg = 'Already exists({0})'.format(trigger['expression'])
            raise Exception(msg)

        params = self.__to_parameters(trigger)

        result = self._do_request('trigger.create', params)
        return result['triggerids'][0] if result else None

    def update_one(self, trigger, triggerid=None):
        if triggerid is None:
            triggerid = self.__get_id(trigger)

        if triggerid is None:
            msg = 'Not exists({0})'.format(trigger['expression'])
            raise Exception(msg)

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
        params = {}
        params['description'] = trigger['description']
        params['expression'] = trigger['expression']
        if 'priority' in trigger:
            params['priority'] = trigger['priority']
        if 'recovery_expression' in trigger:
            params['recovery_expression'] = trigger['recovery_expression']
        if 'manual_close' in trigger:
            params['manual_close'] = trigger['manual_close']

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

    def delete(self, hostname, expressions):
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
