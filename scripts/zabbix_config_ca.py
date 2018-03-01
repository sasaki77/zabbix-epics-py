import argparse

import zbxepics.zbxconfig.provision as provision


def parseArgs():
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('--file', help='JSON file', required=True)
    parser.add_argument('--url', help='URL to zabbix api.')
    parser.add_argument('--user', help='Zabbix user name.')
    parser.add_argument('--password', help='Zabbix user password.')

    return parser.parse_args()


def main():
    args = parseArgs()
    loader = provision.ZabbixProvisionConfigJSON()
    config_data = loader.load_config_from_json(args.file)

    provisioner = provision.ZabbixProvisionCA(args.url, args.user,
                                              args.password)
    provisioner.exec_provision(config_data)


if __name__ == '__main__':
    main()
