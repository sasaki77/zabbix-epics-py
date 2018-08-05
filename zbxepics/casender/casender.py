import time
try:
    import threading
except ImportError:
    import dummy_threading as threading

from pyzabbix import ZabbixMetric, ZabbixSender, ZabbixResponse

from zbxepics.logging import logger
from zbxepics.casender.peekqueue import PriorityPeekQueue
from zbxepics.casender.item import MonitorItemFactory, IntervalItemFactory


class ZabbixSenderCA(object):
    """
    ZabbixSenderCA class, send metrics to Zabbix server.

    Attributes
    ----------
    _monitor_items : list of zbxepics.casender.item.MonitorItem
        list of monitor items
    _interval_item_q : zbxepics.casender.peekqueue.PriorityPeekQueue
        priority queue of interval items
    zbx_sender : pyzabbix.ZabbixSender
        Zabbix sender to send metrics to Zabbix server
    __is_stop : threading.Event
        whether server is stop or not
    __stop_request : bool
        to stop running server
    _is_running : bool
        whether server is running or not
    """

    def __init__(self, zabbix_server='127.0.0.1', zabbix_port=10051,
                 use_config=None, items=None):
        """
        Parameters
        ----------
        zabbix_server : str
            Zabbix server ip address (default is '127.0.0.1')
        zabbix_port : int
            Zabbix server port (default is 10051)
        use_config : str or bool
            Path to zabbix_agentd.conf file to load settings from.
            If value is 'True' then default config path will used:
            /etc/zabbix/zabbix_agentd.conf
        items: dict
            List of sender items.
            (Prerequisite keys: host pv interval, Optional: item_key func)
        """

        self._monitor_items = []
        self._interval_item_q = PriorityPeekQueue()
        self.zbx_sender = ZabbixSender(zabbix_server,
                                       zabbix_port,
                                       use_config)
        self.__is_stop = threading.Event()
        self.__stop_request = False
        self._is_running = False

        if items:
            for item in items:
                self.add_item(item)

    def add_item(self, item):
        """Add sender item to container

        Parameters
        ----------
        item : dict
            dict of item with following keys
            ('host', 'pv', 'interval', 'item_key', 'func')

        Returns
        -------
        item.MonitorItem or item.IntervalItem
            Added item
        """

        try:
            host = item['host']
            pvname = item['pv']
            interval = item['interval']
            item_key = item.get('item_key')

            if interval == 'monitor':
                sender_item = (MonitorItemFactory
                               .create_item(host, pvname, item_key))
                self._monitor_items.append(sender_item)
            else:
                func = item['func']
                sender_item = (IntervalItemFactory
                               .create_item(host, pvname, interval,
                                            func, item_key))
                self._interval_item_q.put((0, sender_item))
        except Exception:
            sender_item = None

        return sender_item

    def __get_interval_items(self):
        """Return a list of items to be executed

        Returns
        -------
        list of item.Intervalitem
            Return a list of items to be executed
        """

        if self._interval_item_q.empty():
            return []

        items = []
        now = int(time.time())
        while now >= self._interval_item_q.peek()[0]:
            _, item = self._interval_item_q.get()
            items.append(item)
            # Rescedule
            runtime = now + item.interval
            self._interval_item_q.put((runtime, item))

        return items

    def _create_metrics(self, items):
        """Return a list of metrics from item

        Parameters
        ----------
        items : list of item.MonitorItem or item.IntervalItem
            items to get metrics

        Returns
        -------
        list of pyzabbix.ZabbixMetric
            a list of metrics from item
        """

        metrics = []

        for item in items:
            try:
                zm = item.get_metrics()
                metrics.extend(zm)
            except Exception:
                pass

        return metrics

    def _send_metrics(self, items):
        """Send metrics to Zabbix server

        Parameters
        ----------
        items : list of item.MonitorItem or item.IntervalItem
        """

        metrics = self._create_metrics(items)
        if not metrics:
            return

        result = self.zbx_sender.send(metrics)
        logger.debug('%s: %s',
                     self.__class__.__name__,
                     result)

    def run(self):
        """Start ca sender server"""

        if (not self._monitor_items
                and self._interval_item_q.empty()):
            # Do not start if items is empty
            raise Exception('Sender process have no items.')

        self._is_running = True

        self.__is_stop.clear()
        try:
            while not self.__stop_request:
                items = []
                items.extend(self._monitor_items)
                items.extend(self.__get_interval_items())

                self._send_metrics(items)

                time.sleep(1)
        except Exception as err:
            logger.error(err)
        finally:
            logger.info('%s: %s',
                        self.__class__.__name__,
                        'Sender process stopped.')
            self.__stop_request = False
            self.__is_stop.set()

        self._is_running = False

    def stop(self):
        """Stop the run loop"""
        self.__stop_request = True
        self.__is_stop.wait()

    @property
    def is_running(self):
        """bool: Whether server is running or not"""
        return self._is_running
