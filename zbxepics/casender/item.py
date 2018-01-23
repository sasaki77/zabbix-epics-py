from pyzabbix import ZabbixMetric
from zbxepics.casender.zbxmath import functions
from zbxepics.logging import logger
from zbxepics.pvsupport import ValQPV


class ZabbixSenderItem(object):

    def __init__(self, host, pvname):
        self.host = str(host)
        self.pv = ValQPV(str(pvname))
        self.item_key = 'EPICS[' + self.pv.pvname + ']'

    def get_metrics(self):
        data = self.pv.get_q_all()

        metrics = []
        for val, timestamp in data:
            zm = ZabbixMetric(self.host, self.item_key, val, int(timestamp))
            metrics.append(zm)

        return metrics


class ZabbixSenderItemInterval(ZabbixSenderItem):

    def __init__(self, host, pvname, interval, func='last'):
        super(ZabbixSenderItemInterval, self).__init__(host, pvname)

        self.interval = float(interval)
        if self.interval < 1.0:
            raise Exception('"interval" must be at least 1 second')

        self._func = functions[func]

    def get_metrics(self):
        data = self.pv.get_q_all()

        vals = [v for v, t in data]
        val = self._func(vals)

        zm = ZabbixMetric(self.host, self.item_key, val)

        return [zm]
