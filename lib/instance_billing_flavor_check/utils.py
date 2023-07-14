# Copyright 2023 SUSE LLC
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
import sys
import requests

from instance_billing_flavor_check.command import Command
from lxml import etree

logger = logging.getLogger(__name__)
log_filename = '/var/log/{}'.format(__name__.split('.')[0])
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format="%(message)s"
)
try:
    from cloudregister.registerutils import get_smt
except ModuleNotFoundError as err:
    pass

REGION_SRV_CLIENT_CONFIG_PATH = '/etc/regionserverclnt.cfg'
BASEPRODUCT_PATH = '/etc/products.d/baseproduct'
ETC_HOSTS_PATH = '/etc/hosts'

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
                rmt_ips_addr.append(etc_hosts_ip_addr)
            except ValueError:
                pass

    return rmt_ips_addr


def _get_ips_from_cloudregister():
    # get a new RMT IP
    server = get_smt(False)
    rmt_ips_addr = []
    if server.get_ipv6():
        rmt_ips_addr.append('[{}]'.format(server.get_ipv6()))
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


def make_request(rmt_ip_addr, metadata, identifier):
    """Return the flavour from the RMT server request."""
    instance_check_url = 'https://{}/api/instance/check'.format(rmt_ip_addr)
    message = None
    billing_check_params = {
        'metadata': metadata,
        'identifier': identifier
    }
    try:
        response = requests.get(
            instance_check_url,
            timeout=2,
            verify=False,
            params=billing_check_params
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
        logger.error(message)
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
    Return 'PAYG' OR 'BYOS'

    Instead of returning a string, this method returns
    a exit code as follows:
    - 10 -> PAYG
    - 11 -> BYOS
    - 12 -> Unknown
    """
    metadata = get_metadata()
    identifier = get_identifier()
    if not metadata or not identifier:
        print('BYOS')
        sys.exit(12)

    rmt_ips_addr = get_rmt_ip_addr()
    if not rmt_ips_addr:
        logger.warning('Instance can be either BYOS or PAYG and not registered')
        print('BYOS')
        sys.exit(12)

    code_flavour = {'PAYG': 10, 'BYOS': 11}
    for rmt_ip_addr in rmt_ips_addr:
        flavour = make_request(rmt_ip_addr, metadata, identifier)
        if flavour:
            print(flavour)
            logger.info(flavour)
            sys.exit(code_flavour.get(flavour))
    print('BYOS')
    sys.exit(12)
