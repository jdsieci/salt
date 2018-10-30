# -*- coding: utf-8 -*-
'''
Support for Bareos backup system.

:depends: Bareos python api
    You can install it using package manager:

    .. code-block:: bash

        salt-call pkg.install python-bareos

:configuration: The following configuration defaults can be
    define (pillar or config files):

    .. code-block:: yaml

        bareos.config:
            address: localhost
            dirname: None
            user: <user agent>
            password: apassword
            port: 9101
            api_kg: None

    Usage can override the config defaults:

    .. code-block:: bash

            salt-call ipmi.get_user api_host=myipmienabled.system
                                    api_user=admin api_pass=pass
                                    uid=1


'''
# Import Python Libs
from __future__ import absolute_import, print_function, unicode_literals
import logging
import json
import re

# Import Salt libs
from salt.ext import six

log = logging.getLogger(__name__)


try:
    import bareos.bsock
    HAS_BAREOS = True
except ImportError:
    HAS_BAREOS = False

__virtualname__ = 'bareos'


def __virtual__():
    if HAS_BAREOS:
        return __virtualname__
    else:
        return False, 'Bareos module cannot be loaded: bareos api not available'


def _get_config(**kwargs):
    '''
    Return configuration
    '''
    config = {
        'address': 'localhost',
        'dirname': None,
        'port': 9101,
        'user': '*UserAgent*',
        'password': '',
    }
    if '__salt__' in globals():
        config_key = '{0}.config'.format(__virtualname__)
        config.update(__salt__['config.get'](config_key, {}))
    for k in set(config) & set(kwargs):
        config[k] = kwargs[k]
    return config


class _BareosConsole(object):

    def __init__(self, **kwargs):
        config = _get_config(**kwargs)
        self.console = bareos.bsock.DirectorConsole(address=config['address'], port=config['port'], name=config['user'],
                                              password=bareos.bsock.Password(config['password']))

    def __enter__(self):
        return self.console

    def __exit__(self, *args):
        del self.console


class _BareosConsoleJson(object):

    def __init__(self, **kwargs):
        config = _get_config(**kwargs)
        self.console = bareos.bsock.DirectorConsoleJson(address=config['address'], port=config['port'], name=config['user'],
                                              password=bareos.bsock.Password(config['password']))

    def __enter__(self):
        return self.console

    def __exit__(self, *args):
        del self.console


def _parse_bareos_config(sconf):
    output = []
    in_section = False
    section = {}
    section_start = re.compile('^\s*(\w)\s*\{')
    for line in sconf.splitlines(sconf):
        if not line: continue
        if section_start.match(line):
            in_section = True
        elif re.match('^\s*}', line):
            output.push(section)
            in_section = False
            section = {}
        elif in_section:
            name, value = line.split('=')
            if not value and section_start.match():
            section[name] = value
    return output

def cmd(command, **kwargs):
    '''
    Run bareos console command and returns raw output
    :param command: command string
    :return: raw command output

    .. code-block:: bash

        salt '*' bareos.cmd 'list clients'
    '''
    with _BareosConsole(**kwargs) as c:
        response = c.call(command)
    return response.decode('utf-8')


def client_list(**kwargs):
    with _BareosConsoleJson(**kwargs) as c:
        res = c.call('list clients')
    return res
