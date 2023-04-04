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

def instance_flavor_check(framework, metadata_path):
    if framework == 'ec2':
        from instance_billing_flavor_check import ec2_instance_check

        metadata = _parse_instance_metadata(metadata_path)
        ec2_instance_metadata = ec2_instance_check.EC2InstanceMetadata(metadata)
        if ec2_instance_metadata.is_payg():
            return 'PAYG'
        else:
            return 'BYOS'
    if framework == 'azure':
        pass
    if framework == 'gce':
        pass
    except Exception:
        return None

def _parse_instance_metadata(metadata_path):
    try:
        with open(metadata_path, 'r') as metadata_file:
            metadata = metadata_file.read()

        start = metadata.index("<document>")
        start = start + len("<document>")
        end = metadata.index("</document>")
        metadata = metadata[start:end]
        return json.loads(metadata)
    except (FileNotFoundError, PermissionError):
        logger.error(f"Could not open the file '{metadata_path}', make sure the path and permissions are right\n")
    except json.decoder.JSONDecodeError as err:
        logger.error(err)
