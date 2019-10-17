import time

import pytest
from epics import PV

from zbxepics.casender.item import MonitorItemFactory, IntervalItemFactory
from zbxepics.casender.item.monitoritem import MonitorItem
from zbxepics.casender.item.intervalitem import IntervalItem


def test_casender_item_init_monitor():
    item = (MonitorItemFactory
            .create_item('host1', 'ET_dummyHost:ai1'))

    assert isinstance(item, MonitorItem)
    assert item.host == 'host1'
    assert isinstance(item.pv, PV)
    assert item.pv.pvname == 'ET_dummyHost:ai1'


def test_casender_item_init_interval():
    item = (IntervalItemFactory
            .create_item('host1', 'ET_dummyHost:ai1',
                                  5, 'last'))

    assert isinstance(item, IntervalItem)
    assert item.host == 'host1'
    assert isinstance(item.pv, PV)
    assert item.pv.pvname == 'ET_dummyHost:ai1'
    assert item.interval == 5


def test_casender_item_init_interval_default():
    item = (IntervalItemFactory
            .create_item('host1', 'ET_dummyHost:ai1'))

    default_interval = IntervalItem.DEFAULT_INTERVAL
    assert item.interval == default_interval

    functions = IntervalItemFactory.list_of_functions()
    default_function = IntervalItemFactory.DEFAULT_FUNCTION
    assert type(item) == functions[default_function]


def test_casender_item_monitor_item_metrics(softioc, caclient):
    item = (MonitorItemFactory
            .create_item('host1', 'ET_dummyHost:long1'))

    pv = item.pv
    pv.wait_for_connection(10)
    test_vals = [v for v in range(5)]
    for val in test_vals:
        pv.put(val, wait=True)
    time.sleep(.05)

    metrics = item.get_metrics()
    assert len(metrics) == 6

    for (zm, tval) in zip(metrics[1:0], test_vals):
        assert zm.host == item.host
        assert zm.key == item.item_key
        assert zm.value == str(tval)


@pytest.mark.parametrize('func,values,result', [
    ('last', [0, 1, 2, 3, 4], '4'),
    ('min', [0, 1, 2, 3, 4], '0'),
    ('max', [0, 1, 2, 3, 4], '4'),
    ('avg', [0, 1, 2, 3, 4], '2.0'),
])
def test_casender_item_interval_item(softioc, caclient, func, values, result):
    item = (IntervalItemFactory
            .create_item('host1', 'ET_dummyHost:long1', func=func))

    pv = item.pv
    pv.wait_for_connection(10)
    for val in values:
        pv.put(val, wait=True)
    time.sleep(.05)

    metrics = item.get_metrics()
    assert len(metrics) == 1
    assert metrics[0].host == item.host
    assert metrics[0].key == item.item_key
    assert metrics[0].value == result

    pv.put(0, wait=True)
    pv.disconnect()
    metrics = item.get_metrics()
    assert metrics == []
