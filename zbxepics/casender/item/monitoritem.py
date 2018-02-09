from queue import Queue

from epics import PV
from pyzabbix import ZabbixMetric


class MonitorItem(object):
    def __init__(self, host, pvname, item_key=None):
        self.host = str(host)
        pvname_ = str(pvname)
        self.pv = PV(pvname_, callback=self._on_value_change)
        self.item_key = item_key
        if self.item_key is None:
            self.item_key = pvname_

        self.__metrics_q = Queue()

    def _on_value_change(self, value=None, timestamp=None, **kw):
        zm = ZabbixMetric(self.host, self.item_key,
                          value, int(timestamp))
        self.__metrics_q.put(zm)

    def get_metrics(self):
        metrics = []
        while not self.__metrics_q.empty():
            metrics.append(self.__metrics_q.get())
        return metrics
