import json
from http.server import HTTPServer, BaseHTTPRequestHandler

from zbxepics.logging.logger import logger


class ZabbixHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        content_len = int(self.headers.get('content-length'))
        message = self._get_request(content_len)
        response = self._create_response(message)
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(response)

    def _get_request(self, content_len):
        try:
            request = self.rfile.read(content_len)
            req_msg = request.decode('utf-8')
            req_json = json.loads(req_msg)
            req_str = json.dumps(req_json, indent=4, separators=(',', ': '))
            logger.debug('Request Body: %s', req_str)
        except Exception:
            logger.error('Unable to parse json: %s', e.message)
            req_msg = None

        return req_msg

    def _create_response(self, message):
        req_json = json.loads(message)

        res_json = {}
        res_json['jsonrpc'] = req_json['jsonrpc']
        res_json['id'] = req_json['id']
        try:
            method = req_json['method']
            if method in self.response_data:
                res_json['result'] = self.response_data[method]
            else:
                raise Exception('Unsupported method')
        except Exception as err:
            error_msg = {'code': -32602,
                         'message': 'Invalid params.',
                         'data': err}
            res_json['error'] = error_msg

        res_str = json.dumps(res_json, indent=4, separators=(',', ': '))
        logger.debug('Response Body: %s', res_str)

        return res_str.encode('utf-8')

    def log_message(self, format, *args):
        pass

    response_data = {
        'user.login': '123456789',
        'hostgroup.get': [{'groupid': '12345'}],
        'hostgroup.create': {'groupids': ['12345']},
        'hostgroup.update': {'groupids': ['12345']},
        'host.get': [{'hostid': '12345'}],
        'host.create': {'hostids': ['12345']},
        'host.update': {'hostids': ['12345']},
        'item.get': [{'itemid': '12345'}],
        'item.create': {'itemids': ['12345']},
        'item.update': {'itemids': ['12345']},
        'application.get': [{
            'applicationid': '12345',
            'name': 'Dummy Status'
            }],
        'application.create': {'applicationids': ['12345']},
        'application.update': {'applicationids': ['12345']},
        'trigger.get': [{
            'triggerid': '12345',
            'expression': '{dummyServerHost:dummy.key.last()}>0'
            }],
        'trigger.create': {'triggerids': ['12345']},
        'trigger.update': {'triggerids': ['12345']},
        'template.get': [{
            'templateid': '12345',
            'host': 'Template dummy'
            }],
        'template.create': {'templateids': ['12345']},
        'template.update': {'templateids': ['12345']}
        }


def main():
    server_address = ('localhost', 30051)
    handler = ZabbixHTTPRequestHandler
    with HTTPServer(server_address, handler) as httpd:
        httpd.serve_forever()


if __name__ == '__main__':
    main()
