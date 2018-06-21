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


def cmd(command, **kwargs):
    with _BareosConsole(**kwargs) as c:
        response = c.call(command)
    return response.decode('utf-8')


def client_list(**kwargs):
    with _BareosConsoleJson(**kwargs) as c:
        res = c.call('list clients')
    return res
