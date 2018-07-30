from setuptools import find_packages, setup

with open('README.md') as f:
        readme = f.read()

with open('LICENSE') as f:
        license = f.read()

setup(
    name='zbxepics',
    version='0.0.1',
    url='https://github.com/sasaki77/zabbix-epics-py',
    license=license,
    maintainer='Shinya Sasaki',
    maintainer_email='shinya.sasaki@kek.jp',
    description='Zabbix-EPICS for Python',
    long_description=readme,
    packages=find_packages(exclude=('tests', 'scripts')),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'future',
        'py-zabbix>=1.1.2',
        'pyepics',
    ],
)
