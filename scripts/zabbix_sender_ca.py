import argparse
from zbxepics import ZabbixSenderCA, ZabbixConfigReaderJSON


def parseArgs():
    default_server = '127.0.0.1'
    default_port = 10051

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-f', '--file', help='JSON, XML file',
                        required=True)
    parser.add_argument('--server', default=default_server,
                        help='Zabbix server ip address.\
                              Default: {0}'.format(default_server),
                        metavar='SERVER_NAME')
    parser.add_argument('--port', default=default_port,
                        help='Zabbix server port. Default: {0}'
                        .format(default_port),
                        metavar='SERVER_PORT')
    parser.add_argument('--config', default=None,
                        help='Path to zabbix_agentd.conf.',
                        metavar='/path/to/zabbix_agentd.conf')

    return parser.parse_args()


def main():
    args = parseArgs()
    reader = ZabbixConfigReaderJSON(args.file)
    items = reader.get_items()
    sender = ZabbixSenderCA(args.server, args.port, args.config, items)
    try:
        sender.run()
    except KeyboardInterrupt:
        pass
    finally:
        sender.stop()


if __name__ == '__main__':
    main()
