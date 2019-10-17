import os
from http.server import HTTPServer
try:
    import threading
except ImportError:
    import dummy_threading as threading
from socketserver import TCPServer
import time

import pytest
from pyzabbix import ZabbixAPI
from epics import ca

from . import zbxstreamserver
from .ioccontrol import IocControl
from .zbxhttpserver import ZabbixHTTPRequestHandler


@pytest.fixture(scope='module')
def softioc():
    dir_path = os.path.dirname(__file__)
    db_file = os.path.join(dir_path, 'test.db')

    ioc_arg_list = ['-m', 'head=ET_dummyHost', '-d', db_file]
    iocprocess = IocControl(arg_list=ioc_arg_list)
    iocprocess.start()

    yield iocprocess

    iocprocess.stop()


@pytest.fixture(scope='session')
def caclient():
    ca.finalize_libca()

    sport = str(IocControl.server_port)
    os.environ['EPICS_CA_AUTO_ADDR_LIST'] = 'NO'
    os.environ['EPICS_CA_ADDR_LIST'] = 'localhost:{}'.format(sport)

    ca.initialize_libca()
    yield
    ca.finalize_libca()


@pytest.fixture(scope='module')
def zbx_stream():
    zbx_host = 'localhost'
    zbx_port = 30051
    server_address = (zbx_host, zbx_port)
    handler = zbxstreamserver.SimpleZabbixServerHandler

    TCPServer.allow_reuse_address = True
    zbxserver = TCPServer(server_address, handler)
    thread_target = zbxserver.serve_forever
    th_server = threading.Thread(target=thread_target)
    th_server.daemon = True
    th_server.start()

    yield (zbx_host, zbx_port)

    zbxserver.shutdown()
    th_server.join()
    zbxserver.server_close()


@pytest.fixture(scope='module')
def zbx_http():
    zbx_host = 'localhost'
    zbx_port = 30051
    handler = ZabbixHTTPRequestHandler
    HTTPServer.allow_reuse_address = True
    httpd = HTTPServer((zbx_host, zbx_port), handler)

    thread_target = httpd.serve_forever
    th_server = threading.Thread(target=thread_target)
    th_server.daemon = True
    th_server.start()

    yield (zbx_host, zbx_port)

    httpd.shutdown()
    th_server.join()
    httpd.server_close()


@pytest.fixture()
def zbx_api():
    api = ZabbixAPI(url='http://localhost:30051')
    return api
