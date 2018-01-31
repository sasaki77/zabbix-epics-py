import time
try:
    import threading
except ImportError:
    import dummy_threading as threading
from pyzabbix import ZabbixMetric, ZabbixSender, ZabbixResponse
from zbxepics.logging import logger
from zbxepics.casender.peekqueue import PriorityPeekQueue
from zbxepics.casender.item import ZabbixSenderItem
from zbxepics.casender.item import ZabbixSenderItemInterval


class ZabbixSenderCA(object):

    """Docstring for ZabbixSenderCA. """

    def __init__(self, zabbix_server='127.0.0.1', zabbix_port=10051,
                 use_config=None, items=None, send_callback=None):
        self._monitor_items = []
        self._interval_item_q = PriorityPeekQueue()
        self.zbx_sender = ZabbixSender(zabbix_server,
                                       zabbix_port,
                                       use_config)
        self.__is_stop = threading.Event()
        self.__stop_request = False
        self._is_running = False

        self.send_callback = None
        if send_callback:
            self.send_callback = send_callback

        if isinstance(items, (tuple, list)):
            for item in items:
                self.add_item(item)

    def add_item(self, item):
        try:
            host = item['host']
            pvname = item['pv']
            interval = item['interval']
            item_key = item['item_key']

            if interval == 'monitor':
                sender_item = ZabbixSenderItem(host, pvname, item_key)
                self._monitor_items.append(sender_item)
            else:
                func = item['func']
                sender_item = ZabbixSenderItemInterval(host, pvname,
                                                       interval, func,
                                                       item_key)
                self._interval_item_q.put((0, sender_item))
        except Exception:
            sender_item = None

        return sender_item

    def __get_interval_items(self):
        items = []
        if not self._interval_item_q.empty():
            now = int(time.time())
            while now >= self._interval_item_q.peek()[0]:
                _, item = self._interval_item_q.get()
                items.append(item)
                # Rescedule
                runtime = now + item.interval
                self._interval_item_q.put((runtime, item))

        return items

    def _create_metrics(self, items):
        metrics = []

        for item in items:
            try:
                zm = item.get_metrics()
                metrics.extend(zm)
            except Exception:
                pass

        return metrics

    def _send_metrics(self, metrics):
        result = self.zbx_sender.send(metrics)
        logger.debug('%s: %s',
                     self.__class__.__name__,
                     result)

        if hasattr(self.send_callback, '__call__'):
            self.send_callback(metrics=metrics, result=result)

    def run(self):
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

                metrics = self._create_metrics(items)

                # Send packet to Zabbix server.
                if metrics:
                    self._send_metrics(metrics)

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
        """Stops the run loop."""
        self.__stop_request = True
        self.__is_stop.wait()

    @property
    def is_running(self):
        return self._is_running
