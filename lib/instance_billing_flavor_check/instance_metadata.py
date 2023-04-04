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


class InstanceMetadata(object):
    def __init__(self, metadata):
        # self._metadata = self._get_instance_metadata()
        self._metadata = metadata

    @property
    def metadata(self):
        """Abstract interface"""
        return self._metadata

    @classmethod
    def is_payg(self):
        """Abstract interface"""
        raise Exception('Not implemented')


    # private methods

    def _get_instance_metadata(self):
        """Abstract interface"""
        raise Exception('Not implemented')
