from queue import Queue
from epics import PV
from zbxepics.logging import logger


class ValQPV(PV):

    def __init__(self, pvname='', connection_callback=None):
        self._q = Queue()

        super(ValQPV, self).__init__(pvname, callback=self._on_value_change,
                                     connection_callback=connection_callback)

    def _on_value_change(self, pvname=None, value=None, timestamp=None, **kw):
        val = (value, timestamp)
        self._q.put(val)
        logger.debug('PV value changed: %s %s', pvname, val)

    def get_q_all(self):
        data = []
        while not self._q.empty():
            data.append(self._q.get())
        return data
