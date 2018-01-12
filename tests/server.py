#!/usr/bin/env python
"""Controls the test Zabbix server"""

from socketserver import TCPServer, StreamRequestHandler
import struct
import json
import zbxepicstests
try:
    import threading
except ImportError:
    import dummy_threading as threading
from zbxepics.logging import logger


class SimpleZabbixServerHandler(StreamRequestHandler):

    def handle(self):
        """Handle multiple requests if necessary."""
        request = self._get_request()
        message = self._create_message(request)
        resp = self._create_response(message)
        packet = self._create_packet(resp)
        self.request.sendall(packet)

    def _receive(self, sock, count):
        """Reads socket to receive data from zabbix client."""
        buf = b''

        while len(buf) < count:
            chunk = sock.recv(count - len(buf))
            if not chunk:
                break
            buf += chunk

        return buf

    def _get_request(self):
        request_header = self._receive(self.connection, 13)
        logger.debug('Request header: %s', request_header)

        if (not request_header.startswith(b'ZBXD\x01')
                or len(request_header) != 13):
            logger.debug('Not valid request.')
            result = False
        else:
            request_len = struct.unpack('<Q', request_header[5:])[0]
            request_body = self.connection.recv(request_len)
            result = json.loads(request_body.decode('utf-8'))
            logger.debug('Data received: %s', result)

        return result

    def _create_message(self, request):
        metrics = request.get('data')

        processed = len(metrics)
        failed = 0
        total = processed
        seconds_spent = 0.0
        msg = ('processed: {p}; failed: {f}; total: {t}; seconds spent: {s}'
               .format(p=processed, f=failed, t=total, s=seconds_spent))

        return msg

    def _create_response(self, msg):
        response = ('{{"info":"{msg}", "response":"success"}}'
                    .format(msg=msg))
        response = response.encode('utf-8')
        logger.debug('Response: %s', response)
        return response

    def _create_packet(self, response):
        data_len = struct.pack('<Q', len(response))
        packet = b'ZBXD\x01' + data_len + response
        logger.debug('Packet [str]: %s', packet)
        return packet


def main():
    host = zbxepicstests.zbx_host
    port = zbxepicstests.zbx_port
    handler = SimpleZabbixServerHandler

    server = TCPServer((host, port), handler)
    try:
        logger.debug('%s: serving at port(%s:%s)',
                     'SimpleZabbixServer', host, port)
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.shutdown()


if __name__ == '__main__':
    main()
