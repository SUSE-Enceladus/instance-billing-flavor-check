#! /usr/bin/python3

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

REGION_SRV_CLIENT_PATH = '/etc/regionserverclnt.cfg'
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

def get_command():
    config = configparser.ConfigParser()
    if config.read(REGION_SRV_CLIENT_PATH):
        try:
            return config['instance']['dataProvider']
        except Exception as err:
            logger.error("Could not parse %s: %s", REGION_SRV_CLIENT_PATH, err)
    else:
        logger.error("Could not read file %s", REGION_SRV_CLIENT_PATH)
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
        logger.error("Could not fetch the metadata after running %s: with status %s", result.error, result.returncode)
        return None


def check_payg_byos():
    """Return 'PAYG' OR 'BYOS'."""
    metadata = get_metadata()
