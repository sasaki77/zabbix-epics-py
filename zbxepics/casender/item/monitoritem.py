from queue import Queue

from epics import PV
from pyzabbix import ZabbixMetric


class MonitorItem(object):
    """
    a class for monitor item

    Attributes
    ----------
    host : str
        host name of item
    pvname : str
        pv name to monitor
    pv : epics.PV
        pv object to be monitored
    item_key : str
        item key of item
    __metric_q : queue.Queue
        queue of ZabbixMetric
    """

    def __init__(self, host, pvname, item_key=None):
        """
        Parameters
        ----------
        host : str
            host name of item
        pv : epics.PV
            pv to monitor
        item_key : str
            item key of item
        """

        self.host = str(host)
        pvname_ = str(pvname)
        self.pv = PV(pvname_, callback=self._on_value_change)
        self.item_key = pvname_ if item_key is None else item_key

        self.__metrics_q = Queue()

    def _on_value_change(self, value=None, timestamp=None, **kw):
        """Callback to be called every monitor update

        Parameters
        ----------
        value : obj
            updated value
        timestamp : float
            timestamp of pv relative to POSIX time origin
        """

        zm = ZabbixMetric(self.host, self.item_key,
                          value, int(timestamp))
        self.__metrics_q.put(zm)

    def get_metrics(self):
        """Get metrics

        Returns
        -------
        list of pyzabbix.ZabbixMetric
            All metrics in queue
        """

        metrics = []
        while not self.__metrics_q.empty():
            metrics.append(self.__metrics_q.get())
        return metrics
