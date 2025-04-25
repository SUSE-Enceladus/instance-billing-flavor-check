# Copyright 2024 SUSE LLC
#
# This file is part of instance-billing-flavor-check
#
# instance-billing-flavor-check is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# instance-billing-flavor-check is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# instance-billing-flavor-check. If not, see <http://www.gnu.org/licenses/>.

import csv
import configparser
import ipaddress
import logging
import os
import requests
import sys
import time

from instance_billing_flavor_check.command import Command
from lxml import etree

logger = logging.getLogger(__name__)
log_filename = '/var/log/{}'.format(__name__.split('.')[0])
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format="%(asctime)s: %(message)s"
)
try:
    from cloudregister.registerutils import (
        get_smt, has_ipv4_access, has_ipv6_access
    )
except ImportError:
    get_smt = None
    has_ipv4_access = None
    has_ipv6_access = None

REGION_SRV_CLIENT_CONFIG_PATH = '/etc/regionserverclnt.cfg'
BASEPRODUCT_PATH = '/etc/products.d/baseproduct'
CACHE_FILE_PATH='/var/cache/instance-billing-flavor-check'
ETC_HOSTS_PATH = '/etc/hosts'
PROXY_CONFIG_PATH = '/etc/sysconfig/proxy'

requests.packages.urllib3.disable_warnings(
    requests.packages.urllib3.exceptions.InsecureRequestWarning
)


def get_instance_data_command():
    config = configparser.ConfigParser()
    if config.read(REGION_SRV_CLIENT_CONFIG_PATH):
        try:
            return config['instance']['dataProvider']
        except Exception as err:
            logger.error(
                "Could not parse %s: %s", REGION_SRV_CLIENT_CONFIG_PATH, err
            )
    else:
        logger.error("Could not read file %s", REGION_SRV_CLIENT_CONFIG_PATH)


def get_metadata():
    """Return instance metadata."""
    command = get_instance_data_command()
    if not command:
        return

    command = command.split(' ')
    result = Command.run(command)
    if result.returncode == 0:
        return result.output

    logger.error(
        "Could not fetch the metadata after running the command '%s': '%s' with status '%s'",
        ' '.join(command),
        result.error,
        result.returncode
    )


def get_identifier():
    """Return the identifier found in /etc/products.d/baseproduct."""
    try:
        with open(BASEPRODUCT_PATH, encoding='utf-8') as stream:
            base_prod_xml = stream.read()
            prod_def_start = base_prod_xml.index('<product')
            product_tree = etree.fromstring(base_prod_xml[prod_def_start:])

        return product_tree.find('name').text.lower()
    except FileNotFoundError:
        logger.error("Could not open '%s' file", BASEPRODUCT_PATH)


def _get_ips_from_etc_hosts():
    try:
        with open(ETC_HOSTS_PATH, encoding='utf-8') as etc_hosts:
            etc_hosts_lines = etc_hosts.readlines()
    except FileNotFoundError:
        logger.error("Could not open '%s' file", ETC_HOSTS_PATH)
        return

    # use present RMT server IP first if registered
    rmt_ips_addr = []
    for etc_hosts_line in etc_hosts_lines:
        if 'susecloud.net' in etc_hosts_line and not etc_hosts_line.startswith('#'):
            # save all the IPs for susecloud.net
            # as with IPv6 enabled there will be more than one line
            etc_hosts_ip_addr = etc_hosts_line.split()[0]
            try:
                ipaddress.ip_address(etc_hosts_ip_addr)
                if etc_hosts_ip_addr not in rmt_ips_addr:
                    rmt_ips_addr.append(etc_hosts_ip_addr)
            except ValueError:
                pass

    return rmt_ips_addr


def _get_ips_from_cloudregister(): # pragma: no cover
    # get a new RMT IP
    server = get_smt(False)
    rmt_ips_addr = []
    if has_ipv6_access() and server.get_ipv6():
        rmt_ips_addr.append('[{}]'.format(server.get_ipv6()))
    if has_ipv4_access():
        rmt_ips_addr.append(server.get_ipv4())

    return rmt_ips_addr


def get_rmt_ip_addr():
    """Return the RMT update server IP the instance is registered to."""
    rmt_ips_addr = _get_ips_from_etc_hosts()

    if not rmt_ips_addr and 'cloudregister' in sys.modules:
        rmt_ips_addr = _get_ips_from_cloudregister()

    if rmt_ips_addr:
        return rmt_ips_addr

    logger.info('Could not determine update server IP address')


def _get_cache_value():
    """
    Get the flavour status from the cache
    """
    flavour = 'BYOS'
    if not os.path.exists(CACHE_FILE_PATH):
        _write_cache(flavour)
    return open(CACHE_FILE_PATH, 'r').read()


def _get_proxies():
    """
    Get proxy info.

    If any proxy has been set up,
    this method returns the proxy info in a dictionary.

    Otherwise, returns an empty dictionary
    """
    if os.environ.get('http_proxy') or os.environ.get('https_proxy'):
        logger.info('Using proxy settings present in the environment.')
        # by default/if None requests relies on the environment variables
        # HTTP_PROXY and HTTPS_PROXY
        return {}

    proxies = {}
    proxy_config = []
    try:
        with open(PROXY_CONFIG_PATH, 'r') as proxy_file:
            proxy_config = proxy_file.readlines()
    except FileNotFoundError:
        pass

    for entry in proxy_config:
        if 'PROXY_ENABLED' in entry and 'no' in entry:
            return None
        if 'HTTP_PROXY' in entry:
            proxies['http_proxy'] = entry.split('"')[1]
        if 'HTTPS_PROXY' in entry:
            proxies['https_proxy'] = entry.split('"')[1]
        if 'NO_PROXY' in entry:
            proxies['no_proxy'] = entry.split('"')[1]

    return proxies


def _write_cache(flavour):
    """Cache the instance flavour"""
    cache = open(CACHE_FILE_PATH, 'w')
    cache.write(flavour)
    cache.close()


def make_request(rmt_ip_addr, metadata, identifier):
    """Return the flavour from the RMT server request."""
    try:
        ip_addr = ipaddress.ip_address(rmt_ip_addr)
    except ValueError:
        logging.error(
            'The RMT IP address {} is not valid.'.format(rmt_ip_addr)
        )
        return

    if isinstance(ip_addr, ipaddress.IPv6Address):
        rmt_ip_addr = '[{}]'.format(rmt_ip_addr)
    instance_check_url = 'https://{}/api/instance/check'.format(rmt_ip_addr)
    message = None
    billing_check_params = {
        'metadata': metadata,
        'identifier': identifier
    }
    proxies = _get_proxies()
    retry_count = 1
    while retry_count != 4:
        try:
            response = requests.get(
                instance_check_url,
                timeout=2,
                verify=False,
                params=billing_check_params,
                proxies=proxies
            )
        except requests.exceptions.HTTPError as err:
            message = 'Http Error:{}'.format(err)
        except requests.exceptions.ConnectionError as err:
            message = 'Error Connecting:{}'.format(err)
        except requests.exceptions.Timeout as err:
            message = 'Timeout Error:{}'.format(err)
        except requests.exceptions.RequestException as err:
            message = 'Request error:{}'.format(err)
        except Exception as err:
            message = 'Unexpected error: {}'.format(err)
    
        if message:
            logger.warning(
                'Attempt {}: failed: {}'.format(retry_count, message)
            )
            if 'Timeout' in message:
                retry_count += 1
                time.sleep(2)
            if 'Timeout' in message or retry_count == 4:
                return

        if response.status_code == 200:
            result = response.json()
            logger.debug(result)
            return result.get('flavor')

    logger.error(
        'Request to check if instance is PAYG/BYOS failed: %s', response.reason
    )


def check_payg_byos():
    """
    Return 'PAYG' OR 'BYOS' and a code

    - (PAYG, 10)
    - (BYOS, 11)
    - (BYOS, 12) Unknown

    When the flavor cannot be reliably determined we declar the instance to be
    BYOS. That the information is not reliable is indicated by the return code.
    """
    flavour = 'BYOS'
    if not (has_ipv6_access() or has_ipv4_access()):
        # instance does not have internet access through IPv4 or IPv6
        _write_cache(flavour)
        return (flavour, 12)
    metadata = get_metadata()
    identifier = get_identifier()
    if not metadata or not identifier:
        logger.warning('No instance metadata and identifier')
        _write_cache(flavour)
        return (flavour, 12)

    rmt_ips_addr = get_rmt_ip_addr()
    if not rmt_ips_addr:
        logger.warning('Instance can be either BYOS or PAYG and not registered')
        _write_cache(flavour)
        return (flavour, 12)

    code_flavour = {'PAYG': 10, 'BYOS': 11}
    for rmt_ip_addr in rmt_ips_addr:
        flavour = make_request(rmt_ip_addr, metadata, identifier)
        if flavour:
            logger.info('Successful server query: {}'.format(flavour))
            _write_cache(flavour)
            return (flavour, code_flavour.get(flavour))
            
    flavour = _get_cache_value()
    logger.info('Using cache value: {}'.format(flavour))
    return (flavour, code_flavour.get(flavour))
