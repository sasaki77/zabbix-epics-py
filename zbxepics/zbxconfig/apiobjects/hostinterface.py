from .apiobject import APIObject
from .host import Host


class HostInterface(APIObject):

    def __init__(self, zbx_api):
        self.__host = Host(zbx_api)
        super(HostInterface, self).__init__(zbx_api)

    def get_interfaces_by_host(self, hostnames, dns=None, ip=None,
                               port=None, output=None):
        hostids = self.__get_host_ids(hostnames)
        params = {}
        params['filter'] = {'hostids': hostids, 'dns': dns,
                            'ip': ip, 'port': port}
        params['output'] = ['interfaceid', 'hostid', 'main', 'type',
                            'useip', 'ip', 'dns', 'port']
        if output is not None:
            params['output'] = output

        result = self._do_request('hostinterface.get', params)
        return result

    def get_id_by_dns(self, hostname, dns_name, port):
        interfaces = self.get_interfaces_by_host([hostname],
                                                 dns=dns_name,
                                                 port=port)
        return interfaces[0]['interfaceid'] if interfaces else None

    def get_id_by_ip(self, hostname, ip_addr, port):
        interfaces = self.get_interfaces_by_host([hostname],
                                                 ip=ip_addr,
                                                 port=port)
        return interfaces[0]['interfaceid'] if interfaces else None

    def __get_host_ids(self, hostnames):
        hosts = self.__host.get_hosts_by_name(hostnames)
        hostids = None
        if hosts:
            hostids = [host['hostid'] for host in hosts]
        return hostids
