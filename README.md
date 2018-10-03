# Zabbix sender for EPICS-CA

This package allows to send metrics to a Zabbix server from EPICS records via Channel Access.

See [docmentation](https://sasaki77.github.io/zabbix-epics-py/)

## Installing

Simple install is below.

```bash
pip install git+https://github.com/sasaki77/zabbix-epics-py.git
```

Or clone this package and install it.

```bash
# clone the repository
git clone https://github.com/sasaki77/zabbix-epics-py
cd zabbix-epics-py
# install zabbix-epics-py
pip install -e .
```

## Usage

Before using this program, you should create hosts and items in Zabbix.
Type of the items must be set to Zabbix trapper.

Below is a simple example usage.
Values of `TEST:PV` are sent to a Zabbix server at 30 sec intervals and metrics are stored to `zabbix-epics-py-test.item` key of `dummyHost`.

```python
>>> from zbxepics import ZabbixSenderCA
>>> host = '127.0.0.1'
>>> port = 10051
>>> config = False
>>> items = [{'host': 'dummyHost', 'pv': 'TEST:PV', "interval": 30, "item_key": 'zabbix-epics-py-test.item', 'func': 'last'}]
>>> sender = ZabbixSenderCA(host, port, config, items)
>>> sender.run()
```

`interval` is an interval in seconds between sending metrics to Zabbix. If `interval` is set to `monitor`, metrics are sent every monitor update.

`func` determines a function to be applied to a monitored value buffer.

Avalilable funcs are below.

- last
- min
- max
- avg

For example, a monitored pv is processed 3 times and its value changed to 1, 2 and 3. Then the value sent to Zabbix is 2 if `func` is set to avg.

## Test

Some part of tests run HTTP server on 30051 port to emulate a Zabbix server.

You should concern localhost http access to test correctly.
(e.g. HTTP proxy settings)

Run without coverage:
```bash
pip install pytest
pytest
```

Run with coverage:
```bash
pip install pytest pytest-cov
pytest --cov gfhttpva
coverage report -m
```
