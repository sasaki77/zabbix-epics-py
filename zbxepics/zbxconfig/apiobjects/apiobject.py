from pyzabbix import ZabbixAPI, ZabbixAPIException

from zbxepics.logging.logger import logger


class APIObject(object):

    def __init__(self, zbx_api):
        self._zbx_api = zbx_api

    def _do_request(self, method, params):
        """Make request to Zabbix API.

        :type method: str
        :param method: ZabbixAPI method, like: `apiinfo.version`.

        :type params: str
        :param params: ZabbixAPI method arguments.

        :rtype: list
        :return: Return list of values in `result`.
        """
        try:
            response = self._zbx_api.do_request(method, params)
            logger.debug("Response data: %s", response)
        except ZabbixAPIException as e:
            logger.error('%s', e.args)
            raise Exception('Invalid request')

        return response['result']
