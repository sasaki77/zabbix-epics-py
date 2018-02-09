try:
    import threading
except ImportError:
    import dummy_threading as threading

from epics import PV
from pyzabbix import ZabbixMetric


class IntervalItem(object):
    DEFAULT_INTERVAL = 30.0

    def __init__(self, host, pvname, interval=None, item_key=None):
        self.host = str(host)
        pvname_ = str(pvname)
        self.pv = PV(pvname_, callback=self._on_value_change)
        self.item_key = item_key
        if self.item_key is None:
            self.item_key = pvname_

        self.interval = interval
        if self.interval is None or self.interval < 1.0:
            self.interval = self.DEFAULT_INTERVAL

        self._value = None
        self.__last_value = None

        self._lock = threading.Lock()

        self._setup()

    def _setup(self):
        """May be overridden by a subclass."""
        pass

    def _on_value_change(self, value=None, timestamp=None, **kw):
        """Called when PV value changed.

        May be overridden by a subclass.

        """
        pass

    def __get_value(self):
        with self._lock:
            if self._value is not None:
                self.__last_value = self._value
                self._value = None
                self._setup()

        if not self.pv.connected or self.__last_value is None:
            return None
        else:
            return self.__last_value

    def get_metrics(self):
        value = self.__get_value()
        if value is None:
            return []
        else:
            zm = ZabbixMetric(self.host, self.item_key, value)
            return [zm]


class IntervalItemHasLast(IntervalItem):

    def _on_value_change(self, value=None, timestamp=None, **kw):
        with self._lock:
            self._value = value


class IntervalItemHasMin(IntervalItem):

    def _on_value_change(self, value=None, timestamp=None, **kw):
        with self._lock:
            if self._value is None:
                self._value = value
            else:
                self._value = min(self._value, value)


class IntervalItemHasMax(IntervalItem):

    def _on_value_change(self, value=None, timestamp=None, **kw):
        with self._lock:
            if self._value is None:
                self._value = value
            else:
                self._value = max(self._value, value)


class IntervalItemHasAvg(IntervalItem):

    def _setup(self):
        self.__sum = 0
        self.__count = 0

    def _on_value_change(self, value=None, timestamp=None, **kw):
        with self._lock:
            self.__sum += value
            self.__count += 1
            self._value = float(self.__sum) / self.__count
