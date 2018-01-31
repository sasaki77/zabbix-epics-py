from pyzabbix import ZabbixMetric
from zbxepics.casender.zbxmath import functions
from zbxepics.logging import logger
from zbxepics.pvsupport import ValQPV


class ZabbixSenderItem(object):

    def __init__(self, host, pvname, item_key=None):
        self.host = str(host)
        pvname_ = str(pvname)
        self.pv = ValQPV(pvname_)
        if item_key:
            self.item_key = str(item_key)
        else:
            self.item_key = 'EPICS[{pvname}]'.format(pvname=pvname_)

    def get_metrics(self):
        data = self.pv.get_q_all()

        metrics = []
        for val, timestamp in data:
            zm = ZabbixMetric(self.host, self.item_key, val, int(timestamp))
            metrics.append(zm)

        return metrics


class ZabbixSenderItemInterval(ZabbixSenderItem):
    DEFAULT_INTERVAL = 30.0
    DEFAULT_FUNCTION = 'last'

    def __init__(self, host, pvname,
                 interval=None, function=None,
                 item_key=None):
        super(ZabbixSenderItemInterval, self).__init__(host, pvname, item_key)

        self.interval = float(interval)
        if (self.interval is None
                or self.interval < 1.0):
            self.interval = self.DEFAULT_INTERVAL

        func = function
        if (func is None
                or func not in functions):
            func = self.DEFAULT_FUNCTION
        self.function = functions[func]

    def get_metrics(self):
        data = self.pv.get_q_all()
        if not data:
            return []

        vals = [v for v, t in data]
        val = self.function(vals)

        zm = ZabbixMetric(self.host, self.item_key, val)

        return [zm]
