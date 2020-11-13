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


class BandwidthGenerator(AzureGenerator):
    """Generator for Bandwidth data."""

    SERVICE_METER = (("Bandwidth", "", "Data Transfer In", "10 GB"), ("Bandwidth", "", "Data Transfer Out - Free", ""))
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
    ADDITIONAL_INFO = (
        {"ConsumptionMeter": "22222222-3333-4444-5555-666666666666"},
        {
            "ImageType": None,
            "ServiceType": None,
            "VMName": None,
            "VMProperties": None,
            "VCPUs": 0,
            "UsageType": "DataTrIn",
        },
        {
            "ImageType": None,
            "ServiceType": None,
            "VMName": None,
            "VMProperties": None,
            "VCPUs": 0,
            "UsageType": "DataTrOut",
            "ConsumptionMeter": "77777777-8888-aaaa-bbbb-cccccccccccc",
        },
    )

    def __init__(self, start_date, end_date, account_info, attributes=None):
        """Initialize the data transfer generator."""
        self._service_name = "Bandwidth"
        super().__init__(start_date, end_date, account_info, attributes)
