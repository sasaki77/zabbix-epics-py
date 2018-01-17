import time
try:
    import threading
except ImportError:
    import dummy_threading as threading
from pyzabbix import ZabbixMetric, ZabbixSender, ZabbixResponse
from zbxepics.logging import logger
from zbxepics.pvsupport import ValQPV
from zbxepics.casender.peekqueue import PriorityPeekQueue
from zbxepics.casender.zbxmath import last, avg


class ZabbixSenderItem(object):
    def __init__(self, host, pvname, interval, func=None):
        self.host = str(host)
        self.pv = ValQPV(str(pvname))
        self.interval = interval
        if func:
            self.func = eval(func)

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
            val = self.func(vals)
            m = ZabbixMetric(self.host, item_key, val)
            metrics.append(m)

        return metrics


class ZabbixSenderCA(object):

    """Docstring for ZabbixSenderCA. """

    def __init__(self, zabbix_server='127.0.0.1', zabbix_port=10051,
                 use_config=None, items=None):
        self._monitor_items = []
        self._interval_item_q = PriorityPeekQueue()
        self.zbx_sender = ZabbixSender(zabbix_server,
                                       zabbix_port,
                                       use_config)
        self.__is_stop = threading.Event()
        self.__stop_request = False
        self._processed = 0
        self._failed = 0
        self._total = 0

        if isinstance(items, (tuple, list)):
            for item in items:
                self.add_item(item)

    def add_item(self, item):
        host = item['host']
        pvname = item['pv']
        interval = item['interval']
        func = item['func'] if 'func' in item else None

        sender_item = ZabbixSenderItem(host, pvname, interval, func)

        if isinstance(interval, str):
            if not interval == 'monitor':
                raise Exception('"%s" is not support'.format(interval))
            self._monitor_items.append(sender_item)
        elif isinstance(interval, (int, float)):
            if interval < 1:
                raise Exception('The interval must be at least 1 second')
            self._interval_item_q.put((0, sender_item))

        return sender_item

    def _create_metrics(self, items):
        metrics = []
        for item in items:
            m = item.get_metrics()
            metrics.extend(m)

        return metrics

    def run(self):
        if (not self._monitor_items
                and self._interval_item_q.empty()):
            # Do not start if items is empty
            logger.error('%s: %s',
                         self.__class__.__name__,
                         'Sender process have no items.')
            return

        self.__is_stop.clear()
        try:
            while not self.__stop_request:
                packet = []

                # Create Zabbix metrics packet for monitor items
                metrics = self._create_metrics(self._monitor_items)
                packet.extend(metrics)

                # Create Zabbix metrics packet for interval items
                if not self._interval_item_q.empty():
                    push_items = []
                    now = int(time.time())
                    while now >= self._interval_item_q.peek()[0]:
                        _, item = self._interval_item_q.get()
                        next_time = now + item.interval
                        self._interval_item_q.put((next_time, item))
                        push_items.append(item)
                    metrics = self._create_metrics(push_items)
                    packet.extend(metrics)

                # Send packet to Zabbix server.
                if packet:
                    result = self.zbx_sender.send(packet)
                    logger.debug('%s: %s',
                                 self.__class__.__name__,
                                 result)
                    self._processed += result.processed
                    self._failed += result.failed
                    self._total += result.total
                time.sleep(1)
        except KeyError:
            logger.error('%s: %s',
                         self.__class__.__name__,
                         'Aborted. Item definition is invalid.')
        finally:
            logger.info('%s: %s',
                        self.__class__.__name__,
                        'Sender process stopped.')
            self.__stop_request = False
            self.__is_stop.set()

    def stop(self):
        """Stops the run loop."""
        self.__stop_request = True
        self.__is_stop.wait()

    @property
    def processed(self):
        return self._processed

    @property
    def failed(self):
        return self._failed

    @property
    def total(self):
        return self._total
