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


class VNGenerator(AzureGenerator):
    """Generator for Virtual Network data."""

    SERVICE_METER = (("IP Addresses", "IP Addresses", "Dynamic Public IP - Free", ""),)
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
    ADDITIONAL_INFO = ({"ConsumptionMeter": "f114cb19-ea64-40b5-bcd7-aee474b62853"},)

    def __init__(self, start_date, end_date, account_info, attributes=None):
        """Initialize the data transfer generator."""
        self._service_name = "Virtual Network"
        super().__init__(start_date, end_date, account_info, attributes)
