try:
    import threading
except ImportError:
    import dummy_threading as threading

from epics import PV
from pyzabbix import ZabbixMetric


class IntervalItem(object):
    """
    a class for interval item

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
    interval : float
        interval in senconds to send
    value : obj
        value to be got
    __last_value : obj
        last got value
    _lock : threading.Lock()
        lock for value
    """

    DEFAULT_INTERVAL = 30.0

    def __init__(self, host, pvname, interval=30.0, item_key=None):
        """
        Parameters
        ----------
        host : str
            host name of item
        pvname : str
            pv name to monitor
        interval : float
            interval in senconds to send (default is 30.0)
        item_key : str
            item key of item (default is None)
        """

        self.host = str(host)
        pvname_ = str(pvname)
        self.pv = PV(pvname_,
                     connection_callback=self._on_connection_change,
                     callback=self._on_value_change)
        self.item_key = pvname_ if item_key is None else item_key

        self.interval = interval
        if self.interval is None or self.interval < 1.0:
            self.interval = self.DEFAULT_INTERVAL

        self._value = None
        self.__last_value = None

        self._lock = threading.Lock()

        self._setup()

    def _setup(self):
        """May be overridden by a subclass"""
        pass

    def _on_connection_change(self, pvname=None, conn=None, **kws):
        """Callback to be called every connection state change

        Parameters
        ----------
        pvname : str
            the name of the pv
        conn : bool
            specifying whether the PV is now connected

        Notes
        -----
            May be overridden by a subclass.
        """

        if not conn:
            self._value = None
            self._setup()

    def _on_value_change(self, value=None, timestamp=None, **kw):
        """Callback to be called every monitor update

        Parameters
        ----------
        value : obj
            updated value
        timestamp : float
            timestamp of pv relative to POSIX time origin

        Notes
        -----
            May be overridden by a subclass.
        """

        pass

    def __get_value(self):
        """Get current value

        Returns
        -------
        obj
            current value if value is updated else last value
        """

        if not self.pv.connected:
            return None

        with self._lock:
            if self._value is not None:
                self.__last_value = self._value
                self._value = None
                self._setup()

        return self.__last_value

    def get_metrics(self):
        """Get Zabbix Metircs

        Returns
        -------
        list of pyzabbix.ZabbixMetric
            list of zabbix metric
        """

        value = self.__get_value()
        if value is None:
            return []

        zm = ZabbixMetric(self.host, self.item_key, value)
        return [zm]

    def __lt__(self, other):
        return True


class IntervalItemLast(IntervalItem):
    """a class for last interval item"""

    def _on_value_change(self, value=None, timestamp=None, **kw):
        """Callback to be called every monitor update

        Parameters
        ----------
        value : obj
            updated value
        timestamp : float
            timestamp of pv relative to POSIX time origin
        """

        with self._lock:
            self._value = value


class IntervalItemMin(IntervalItem):
    """a class for min interval item"""

    def _on_value_change(self, value=None, timestamp=None, **kw):
        """Callback to be called every monitor update

        Parameters
        ----------
        value : obj
            updated value
        timestamp : float
            timestamp of pv relative to POSIX time origin
        """

        with self._lock:
            self._value = (value if self._value is None
                           else min(self._value, value))


class IntervalItemMax(IntervalItem):
    """a class for max interval item"""

    def _on_value_change(self, value=None, timestamp=None, **kw):
        """Callback to be called every monitor update

        Parameters
        ----------
        value : obj
            updated value
        timestamp : float
            timestamp of pv relative to POSIX time origin
        """

        with self._lock:
            self._value = (value if self._value is None
                           else max(self._value, value))


class IntervalItemAvg(IntervalItem):
    """
    a class for average interval item

    Attributes
    ----------
    sum : int or float
        sum of values
    count : int
        counts of value change
    """

    def _setup(self):
        """Set up to initialize"""
        self.__sum = 0
        self.__count = 0

    def _on_value_change(self, value=None, timestamp=None, **kw):
        """Callback to be called every monitor update

        Parameters
        ----------
        value : obj
            updated value
        timestamp : float
            timestamp of pv relative to POSIX time origin
        """

        with self._lock:
            self.__sum += value
            self.__count += 1
            self._value = float(self.__sum) / self.__count
