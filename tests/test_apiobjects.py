import zbxepics.zbxconfig.apiobjects as apiobjects


def test_apiobjects_init_hostgroup(zbx_http, zbx_api):
    hostgroup = apiobjects.HostGroup(zbx_api)
    assert hostgroup is not None


def test_apiobjects_hostgroup_create(zbx_http, zbx_api):
    hostgroup = apiobjects.HostGroup(zbx_api)

    params = {'name': 'Dummy Hosts'}
    groupid = hostgroup.create_one(params)
    assert groupid is None


def test_apiobjects_hostgroup_update(zbx_http, zbx_api):
    hostgroup = apiobjects.HostGroup(zbx_api)

    params = {'name': 'Dummy Hosts'}
    groupid = hostgroup.update_one(params)
    assert groupid is not None


def test_apiobjects_init_host(zbx_http, zbx_api):
    host = apiobjects.Host(zbx_api)
    assert host is not None


def test_apiobjects_host_create(zbx_http, zbx_api):
    host = apiobjects.Host(zbx_api)

    interface = {'type': 1, 'main': 1, 'useip': 1,
                 'ip': '192.168.1.10', 'dns': '', 'port': '10050'}
    params = {'name': 'dummyServerHost',
              'interfaces': [interface],
              'groups': ['Dummy Group']}
    hostid = host.create_one(params)
    assert hostid is None


def test_apiobjects_host_update(zbx_http, zbx_api):
    host = apiobjects.Host(zbx_api)

    interface = {'type': 1, 'main': 1, 'useip': 0,
                 'ip': '192.168.1.10', 'dns': 'dummyServerHost',
                 'port': '10050'}
    params = {'name': 'dummyServerHost',
              'interfaces': [interface],
              'groups': ['Dummy Group']}
    hostid = host.update_one(params)
    assert hostid is not None


def test_apiobjects_init_item(zbx_http, zbx_api):
    item = apiobjects.Item(zbx_api)
    assert item is not None


def test_apiobjects_item_create(zbx_http, zbx_api):
    item = apiobjects.Item(zbx_api)

    params = {'host': 'dummyServerHost',
              'name': 'Dummy Item',
              'key_': 'dummy.key',
              'type': 2,
              'value_type': 0,
              'trapper_hosts': ''}
    itemid = item.create_one(params)
    assert itemid is None


def test_apiobjects_item_update(zbx_http, zbx_api):
    item = apiobjects.Item(zbx_api)

    params = {'host': 'dummyServerHost',
              'name': 'Dummy Item',
              'key_': 'dummy.key',
              'type': 2,
              'value_type': 0,
              'trapper_hosts': '',
              'applications': ['Dummy Status']}
    itemid = item.update_one(params)
    assert itemid is not None


def test_apiobjects_init_application(zbx_http, zbx_api):
    app = apiobjects.Application(zbx_api)
    assert app is not None


def test_apiobjects_application_create(zbx_http, zbx_api):
    app = apiobjects.Application(zbx_api)

    params = {'name': 'Dummy Status',
              'host': 'dummyServerHost'}
    appid = app.create_one(params)
    assert appid is None


def test_apiobjects_application_update(zbx_http, zbx_api):
    app = apiobjects.Application(zbx_api)

    params = {'name': 'Dummy Status',
              'host': 'dummyServerHost',
              'new_name': 'Dummy Status2'}
    appid = app.update_one(params)
    assert appid is not None


def test_apiobjects_init_trigger(zbx_http, zbx_api):
    trigger = apiobjects.Trigger(zbx_api)
    assert trigger is not None


def test_apiobjects_trigger_create(zbx_http, zbx_api):
    trigger = apiobjects.Trigger(zbx_api)

    params = {'host': 'dummyServerHost',
              'description': 'Dummy Trigger',
              'expression': '{dummyServerHost:dummy.key.last()}>0',
              'severity': '3',
              'recovery_expression': '',
              'manual_close': '0'}
    triggerid = trigger.create_one(params)
    assert triggerid is None


def test_apiobjects_trigger_update(zbx_http, zbx_api):
    trigger = apiobjects.Trigger(zbx_api)

    params = {'host': 'dummyServerHost',
              'description': 'Dummy Trigger',
              'expression': '{dummyServerHost:dummy.key.last()}>0',
              'severity': '1',
              'recovery_expression': '',
              'manual_close': '0'}
    triggerid = trigger.update_one(params)
    assert triggerid is not None


def test_apiobjects_init_template(zbx_http, zbx_api):
    template = apiobjects.Template(zbx_api)
    assert template is not None


def test_apiobjects_template_create(zbx_http, zbx_api):
    template = apiobjects.Template(zbx_api)

    params = {'name': 'Template dummy',
              'groups': ['Template/Dummy']}
    templateid = template.create_one(params)
    assert templateid is None


def test_apiobjects_template_update(zbx_http, zbx_api):
    template = apiobjects.Template(zbx_api)

    params = {'name': 'Template dummy',
              'groups': ['Template/Dummy'],
              'hosts': ['dummyServerHost']}
    templateid = template.update_one(params)
    assert templateid is not None
