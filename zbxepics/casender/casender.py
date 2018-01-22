import time
try:
    import threading
except ImportError:
    import dummy_threading as threading
from pyzabbix import ZabbixMetric, ZabbixSender, ZabbixResponse
from zbxepics.logging import logger
from zbxepics.pvsupport import ValQPV
from zbxepics.casender.peekqueue import PriorityPeekQueue
from zbxepics.casender.zbxmath import functions


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
        self._is_running = False
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

        if interval == 'monitor':
            self._monitor_items.append(sender_item)
        else:
            self._interval_item_q.put((0, sender_item))

        return sender_item

    def __get_interval_tasks(self):
        tasks = []
        if not self._interval_item_q.empty():
            now = int(time.time())
            while now >= self._interval_item_q.peek()[0]:
                _, item = self._interval_item_q.get()
                tasks.append(item)
                # Rescedule
                runtime = now + item.interval
                self._interval_item_q.put((runtime, item))

        return tasks

    def _create_metrics(self, items):
        metrics = []

        for item in items:
            m = item.get_metrics()
            metrics.extend(m)

        return metrics

    def _send_metrics(self, metrics):
        result = self.zbx_sender.send(metrics)
        logger.debug('%s: %s',
                     self.__class__.__name__,
                     result)
        self._processed += result.processed
        self._failed += result.failed
        self._total += result.total

    def run(self):
        if (not self._monitor_items
                and self._interval_item_q.empty()):
            # Do not start if items is empty
            raise Exception('Sender process have no items.')

        self._is_running = True

        self.__is_stop.clear()
        try:
            while not self.__stop_request:
                item_tasks = []
                item_tasks.extend(self._monitor_items)
                item_tasks.extend(self.__get_interval_tasks())

                metrics = self._create_metrics(item_tasks)

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
    def processed(self):
        return self._processed

    @property
    def failed(self):
        return self._failed

    @property
    def total(self):
        return self._total

    @property
    def is_running(self):
        return self._is_running
