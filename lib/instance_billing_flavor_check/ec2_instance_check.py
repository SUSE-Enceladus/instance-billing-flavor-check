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

# import ec2metadata

import json
from ec2metadata import EC2Metadata

from instance_check.instancemetadata import InstanceMetadata


class EC2InstanceMetadata(InstanceMetadata):
    def is_payg(self):
        # check billingProducts marketing_Products
        # if null -> BYOS
        return self._metadata.get('billingProducts')

    def _get_instance_metadata(self):
        """Retrive and cache the instance identity document (IID)"""
        meta = EC2Metadata(api='latest')
        return json.loads(meta.get('document'))
