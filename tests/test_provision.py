import os

import zbxepics.zbxconfig.provision as provision


def test_load_config():
    dir_path = os.path.dirname(__file__)
    config_file = os.path.join(dir_path, 'test_zbxconfig.json')
    loader = provision.ZabbixProvisionConfigJSON()
    config_data = loader.load_config_from_json(config_file)

    assert config_data is not None

    fileds = ['hostgroups', 'hosts', 'templates']
    assert sorted(config_data.keys()) == sorted(fileds)


def testA_init(zbx_http):
    host, port = zbx_http
    url = 'http://{host}:{port}'.format(host=host, port=port)
    provisioner = provision.ZabbixProvisionCA(url=url)

    assert provisioner is not None


def test_set_hostgroups(zbx_http):
    host, port = zbx_http
    url = 'http://{host}:{port}'.format(host=host, port=port)
    provisioner = provision.ZabbixProvisionCA(url=url)

    params = [{'name': 'Dummy Group'}]
    provisioner.set_hostgroups(params)
