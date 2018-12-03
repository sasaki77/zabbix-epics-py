import time
try:
    import threading
except ImportError:
    import dummy_threading as threading

import pytest

from . import zbxstreamserver
from zbxepics.casender import ZabbixSenderCA
from zbxepics.casender.item.monitoritem import MonitorItem
from zbxepics.casender.item.intervalitem import IntervalItem


def test_casender_init():
    sender = ZabbixSenderCA('testserver.com', 12345)

    zbx_sender = sender.zbx_sender
    host, port = zbx_sender.zabbix_uri[0]
    assert host == 'testserver.com'
    assert port == 12345


@pytest.mark.parametrize('interval,func,item_type', [
    ('monitor', None, MonitorItem),
    (10, 'last', IntervalItem),
])
def test_casender_add_item(interval, func, item_type):
    item = {'host': 'dummyServerHost', 'pv': 'ET_dummyHost:ai1'}
    item['interval'] = interval
    if func:
        item['func'] = func

    sender = ZabbixSenderCA('testserver.com', 12345)
    sender_item = sender.add_item(item)

    assert isinstance(sender_item, item_type)


def test_casender_add_item_err():
    item = {'host': 'dummyServerHost',
            'pv': 'ET_dummyHost:ai1'}
    sender = ZabbixSenderCA('testserver.com', 12345)
    sender_item = sender.add_item(item)

    assert sender_item is None


def test_casender_run_without_items():
    sender = ZabbixSenderCA('testserver.com', 12345)
    with pytest.raises(Exception):
        sender.run()


def test_casender_stop_request():
    item = {'host': 'dummyServerHost',
            'pv': 'ET_dummyHost:ai',
            'interval': 'monitor'}

    sender = ZabbixSenderCA('testserver.com', 12345)
    sender.add_item(item)

    th_sender = threading.Thread(target=sender.run)
    th_sender.daemon = True
    th_sender.start()

    time.sleep(1)
    assert sender.is_running is True
    sender.stop()
    assert sender.is_running is False

    th_sender.join()


def test_casender_sender_ca(softioc, caclient, zbx_stream):
    item = {'host': 'dummyServerHost',
            'pv': 'ET_dummyHost:long1',
            'interval': 'monitor'}

    zbx_host, zbx_port = zbx_stream
    sender = ZabbixSenderCA(zbx_host, zbx_port)
    sender_item = sender.add_item(item)

    th_sender = threading.Thread(target=sender.run)
    th_sender.daemon = True
    th_sender.start()

    pv = sender_item.pv
    for i in range(5):
        pv.put(i, wait=True)
    time.sleep(1)

    sender.stop()
    th_sender.join()

    assert zbxstreamserver.metrics_received == 5
