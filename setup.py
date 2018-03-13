#!/usr/bin/env python

from distutils.core import setup

setup(name='zbxepics',
      version='0.0.1',
      description='Zabbix-EPICS for Python',
      author='Masaya Hirose',
      author_email='kan-hiro@post.kek.jp',
      packages=['zbxepics', 'zbxepics.casender', 'zbxepics.casender.item',
                'zbxepics.logging', 'zbxepics.zbxconfig',
                'zbxepics.zbxconfig.apiobjects'])
