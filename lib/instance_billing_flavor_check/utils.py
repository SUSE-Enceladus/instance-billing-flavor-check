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
import logging
import sys
import requests

from instance_billing_flavor_check.command import Command

REGION_SRV_CLIENT_CONFIG_PATH = '/etc/regionserverclnt.cfg'
ETC_OS_RELEASE_PATH = '/etc/os-release'
ETC_HOSTS_PATH = '/etc/hosts'

logger = logging.getLogger(__name__)
logging.basicConfig(
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('instance-billing-flavor-check.log', mode='w'),
    ],
    level=logging.INFO,
    format="%(message)s"
)

def get_instance_data_command():
    config = configparser.ConfigParser()
    if config.read(REGION_SRV_CLIENT_CONFIG_PATH):
        try:
            return config['instance']['dataProvider']
        except Exception as err:
            logger.error("Could not parse %s: %s", REGION_SRV_CLIENT_CONFIG_PATH, err)
    else:
        logger.error("Could not read file %s", REGION_SRV_CLIENT_CONFIG_PATH)
    return None



def get_metadata():
    command = get_command()
    if not command:
        return None

    command = command.split(' ')
    result = Command.run(command)
    if result.returncode == 0:
        return result.output
    else:
        logger.error(
            "Could not fetch the metadata after running the command '%s': '%s' with status '%s'",
            ' '.join(command),
            result.error,
            result.returncode
        )
        return None

def get_identifier():
    try:
        with open(ETC_OS_RELEASE_PATH) as stream:
            csv_reader = csv.reader(stream, delimiter="=")
            os_release = dict(csv_reader)
    except FileNotFoundError:
        logger.error("Could not open '%s' file", ETC_RELEASE_PATH)
        syst.exit(1)

    return os_release.get('NAME')

def get_rmt_ip_addr():
    """ Return the RMT update server IP the instance is registered to."""
    try:
        with open(ETC_HOSTS_PATH) as etc_hosts:
            etc_hosts_lines = etc_hosts.readlines()
    except FileNotFoundError:
        logger.error("Could not open '%s' file", ETC_HOSTS_PATH)
        syst.exit(1)

    for etc_hosts_line in etc_hosts_lines:
        if 'susecloud.net' in etc_hosts_line:
            return etc_hosts_line.split('\t')[0]


def make_request(rmtt_ip_addr, metadata, identifier):
    instance_check_url = f"https://{rmt_ip_addr}/api/instance/check"
    requests.packages.urllib3.disable_warnings(
        requests.packages.urllib3.exceptions.InsecureRequestWarning
    )
    message = None
    try:
        response = requests.get(
            instance_check_url,
            timeout=2,
            verify=False,
            metadata=metadata,
            identifer=identifier
        )
    except requests.exceptions.HTTPError as err:
        message = f"Http Error:{err}"
    except requests.exceptions.ConnectionError as err:
        message = f"Error Connecting:{err}"
    except requests.exceptions.Timeout as err:
        message = f"Timeout Error:{err}"
    except requests.exceptions.RequestException as err:
        message = f"Unexpected error:{err}"

    if message:
        logger.error(message)
        sys.exit(1)
    if response.status_code == 200:
        result = response.json()
        logger.debug(result)
        return result.get('flavor')

    logger.error(
        'Request to check if instance is PAYG/BYOS failed: %s', response.reason
    )

def check_payg_byos():
    """Return 'PAYG' OR 'BYOS'."""
    metadata = get_metadata()
    identifier = get_identifier()
    if not metadata or not identifier:
        sys.exit(1)

    rmt_ip_addr = get_rmt_ip_addr()
    if not rmt_ip_addr:
        logger.warning('Instance can be either BYOS or PAYG and not registered')
        sys.exit(0)

    return make_request(rmtt_ip_addr, metadata, identifier)
