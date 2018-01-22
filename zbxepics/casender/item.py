from pyzabbix import ZabbixMetric
from zbxepics.casender.zbxmath import functions
from zbxepics.logging import logger
from zbxepics.pvsupport import ValQPV


class ZabbixSenderItem(object):

    def __init__(self, host, pvname, interval, func=None):
        self.host = str(host)
        self.pv = ValQPV(str(pvname))

        if isinstance(interval, str):
            if not interval == 'monitor':
                raise Exception('"%s" is not support'.format(interval))
        elif isinstance(interval, (int, float)):
            if interval < 1:
                raise Exception('"interval" must be at least 1 second')
            # Check the function
            if func and func in functions:
                self._func = functions[func]
            else:
                raise Exception('Invalid function (%s)', func)
        else:
            raise TypeError('"interval" must be a string or integer/float')

        self.interval = interval

    def get_metrics(self):
        metrics = []

        data = self.pv.get_q_all()
        if not data:
            return metrics

        item_key = 'EPICS[' + self.pv.pvname + ']'
        if self.interval == 'monitor':
            for val, timestamp in data:
                m = ZabbixMetric(self.host, item_key, val, int(timestamp))
                metrics.append(m)
        else:
            vals = [v for v, t in data]
            val = self._func(vals)
            m = ZabbixMetric(self.host, item_key, val)
            metrics.append(m)

        return metrics
