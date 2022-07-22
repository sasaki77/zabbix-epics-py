from setuptools import find_packages, setup

with open('README.md') as f:
    readme = f.read()

setup(
    name='zabbix-epics-py',
    version='1.0.0',
    url='https://github.com/sasaki77/zabbix-epics-py',
    maintainer='Shinya Sasaki',
    description='Zabbix-EPICS for Python',
    long_description=readme,
    long_description_content_type='text/markdown',
    packages=find_packages(exclude=('tests', 'scripts')),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'future',
        'py-zabbix>=1.1.2',
        'pyepics',
        ],
    extras_require={
        'develop': [
            'pytest',
            'pytest-cov',
            'pycodestyle'
            ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
