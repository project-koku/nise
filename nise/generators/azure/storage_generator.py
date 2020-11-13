#
# Copyright 2018 Red Hat, Inc.
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


class StorageGenerator(AzureGenerator):
    """Generator for Storage data."""

    SERVICE_METER = (
        ("General Block Blob", "General Block Blob", "Write Operations", "100000000"),
        ("General Block Blob", "General Block Blob", "Read Operations", "100000000"),
        ("General Block Blob", "General Block Blob", "Delete Operations", "100000000"),
        ("General Block Blob", "General Block Blob", "List and Create Container Operations", "100000000"),
        ("General Block Blob", "General Block Blob", "GRS Write Operations", "100000000"),
        ("Blob Storage", "Tiered Block Blob", "Hot RA-GRS Data Stored", "100 GB/Month"),
        ("Blob Storage", "Tiered Block Blob", "Hot GRS Write Operations", "1000000"),
        ("Blob Storage", "Tiered Block Blob", "Hot LRS Data Stored - Free", ""),
        ("Blob Storage", "Tiered Block Blob", "Hot LRS Write Operations - Free", ""),
        ("Blob Storage", "Tiered Block Blob", "Hot Read Operations - Free", ""),
        ("Blob Storage", "Tiered Block Blob", "All Other Operations", "1000000"),
        ("Storage - Bandwidth", "Bandwidth", "Geo-Replication Data transfer", "100 GB"),
        ("Storage - Bandwidth", "Bandwidth", "Geo-Replication v2 Data transfer", "100 GB"),
        ("Tables", "Tables", "GRS Batch Write Operations", "100000000"),
        ("Tables", "Tables", "Batch Write Operations", "100000000"),
        ("Tables", "Tables", "Write Operations", ""),
        ("Tables", "Tables", "Read Operations", "1000000"),
        ("Tables", "Tables", "LRS Data Stored", "100 GB/Month"),
        ("Tables", "Tables", "RA-GRS Data Stored", "100 GB/Month"),
        ("Standard SSD Managed Disks", "Standard SSD Managed Disks", "E4 Disks", "1 /Month"),
        ("Standard SSD Managed Disks", "Standard SSD Managed Disks", "Disk Operations", "100000000"),
        ("Premium SSD Managed Disks", "Premium SSD Managed Disks", "P10 Disks", ""),
        ("Premium SSD Managed Disks", "Premium SSD Managed Disks", "Disk Operations", ""),
        ("Standard Page Blob", "Standard Page Blob", "Disk Read Operations", "100000000"),
        ("Standard Page Blob", "Standard Page Blob", "Disk Write Operations", "100000000"),
        ("Standard Page Blob", "Standard Page Blob", "LRS Data Stored", "100 GB/Month"),
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

    def __init__(self, start_date, end_date, account_info, attributes=None):
        """Initialize the data transfer generator."""
        self._service_name = "Storage"
        super().__init__(start_date, end_date, account_info, attributes)
