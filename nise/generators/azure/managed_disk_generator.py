#
# Copyright 2024 Red Hat, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
"""Module for azure bandwidth data generation."""

from nise.generators.azure.azure_generator import AzureGenerator


class ManagedDiskGenerator(AzureGenerator):
    """Generator for Storage data."""

    # service_tier, meter_subject, meter_name, units_of_measure
    SERVICE_METER = (
        ("Standard SSD Managed Disks", "Standard SSD Managed Disks", "E4 Disks", "1 /Month"),
        ("Standard SSD Managed Disks", "Standard SSD Managed Disks", "Disk Operations", "100000000"),
        ("Premium SSD Managed Disks", "Premium SSD Managed Disks", "P10 Disks", ""),
        ("Premium SSD Managed Disks", "Premium SSD Managed Disks", "Disk Operations", ""),
    )
    SERVICE_INFO_2 = [None]
    EXAMPLE_RESOURCE = (
        ("RG1", "mysa1"),
        ("RG1", "costmgmtacct1234"),
        ("RG2", "mysa1"),
        ("RG2", "costmgmtacct1234"),
        ("costmgmt", "mysa1"),
        ("costmgmt", "costmgmtacct1234"),
        ("hccm", "mysa1"),
        ("hccm", "costmgmtacct1234"),
    )
    ADDITIONAL_INFO = [None]

    def __init__(self, start_date, end_date, currency, account_info, attributes=None):
        """Initialize the data transfer generator."""
        self._service_name = "Storage"
        super().__init__(start_date, end_date, currency, account_info, attributes)
