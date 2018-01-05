import time
from pyzabbix import ZabbixMetric, ZabbixSender, ZabbixResponse
from zbxepics.logging import logger
from zbxepics.pvsupport import ValQPV
from zbxepics.casender.peekqueue import PriorityPeekQueue
from zbxepics.casender.zbxmath import last, avg


class ZabbixSenderCA(object):

    """Docstring for ZabbixSenderCA. """

    def __init__(self, zabbix_server="127.0.0.1", zabbix_port=10051,
                 use_config=None, items=None):
        self._monitor_items = []
        self._interval_item_q = PriorityPeekQueue()
        self.zbx_sender = ZabbixSender(zabbix_server,
                                       zabbix_port,
                                       use_config)
        if items is not None:
            self.add_items(items)

    def add_item(self, item):
        try:
            if item["interval"] == "monitor":
                self._monitor_items.append(item)
            else:
                self._interval_item_q.put((0, item))
        except KeyError as e:
            logger.error("%s: %s",
                         self.__class__.__name__,
                         e.message)

    def add_items(self, items):
        for item in items:
            self.add_item(item)

    def _create_metrics(self, items):
        metrics = []

        for item in items:
            pv = item["pv"]
            data = pv.get_q_all()
            if not data:
                continue

            host = item["host"]
            pvname = pv.pvname
            item_key = "EPICS[" + pvname + "]"
            interval = item["interval"]
            if interval == "monitor":
                for val, timestamp in data:
                    m = ZabbixMetric(host, item_key, val, int(timestamp))
                    metrics.append(m)
            else:
                try:
                    vals = [v for v, t in data]
                    val = eval(item["func"])(vals)
                    metrics.append(ZabbixMetric(host, item_key, val))
                except NameError as e:
                    logger.error("%s: (%s) %s",
                                 self.__class__.__name__,
                                 pvname,
                                 e.message)

        return metrics

    def run(self):
        if (not self._monitor_items
                and self._interval_item_q.empty()):
            # Do not start if items is empty
            logger.error("%s: %s",
                         self.__class__.__name__,
                         "Sender process have no items.")
            return

        try:
            while True:
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
                        next_time = now + item["interval"]
                        self._interval_item_q.put((next_time, item))
                        push_items.append(item)
                    metrics = self._create_metrics(push_items)
                    packet.extend(metrics)

                # Send packet to Zabbix server.
                if packet:
                    result = self.zbx_sender.send(packet)
                    logger.debug("%s: %s",
                                 self.__class__.__name__,
                                 result)
                time.sleep(1)
        except KeyError:
            logger.error("%s: %s",
                         self.__class__.__name__,
                         "Aborted. Item definition is invalid.")
        except KeyboardInterrupt:
            logger.info("%s: %s.",
                        self.__class__.__name__,
                        "Sender process stopped.")
