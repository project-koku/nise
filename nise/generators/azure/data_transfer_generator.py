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

from random import choice

from nise.generators.azure.azure_generator import AzureGenerator


class DTGenerator(AzureGenerator):
    """Generator for Virtual Machine data."""

    ACCTS_STR = {
        "Virtual Network": ("microsoft.compute", "publicIPAddresses"),
    }
    SERVICE_METER = {
        "in": (
            "Virtual Network Private Link",
            "Virtual Network Private Link",
            "Standard Data Processed - Ingress",
            "1 GB",
        ),
        "out": (
            "Virtual Network Private Link",
            "Virtual Network Private Link",
            "Standard Data Processed - Egress",
            "1 GB",
        ),
    }
    SERVICE_FAMILIES = "Networking"
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
    ADDITIONAL_INFO = {
        "Standard Data Processed - Egress": {
            "DataTransferDirection": "DataTrOut",
        },
        "Standard Data Processed - Ingress": {
            "DataTransferDirection": "DataTrIn",
        },
    }

    def __init__(self, start_date, end_date, currency, account_info, attributes=None):
        """Initialize the data transfer generator."""
        self._service_name = "Virtual Network"
        super().__init__(start_date, end_date, currency, account_info, attributes)

    def _get_additional_info(self, meter_name):
        """Pick additional info."""
        return self.ADDITIONAL_INFO.get(meter_name, {})

    def _get_cached_meter_values(self, meter_id, service_meter):
        """Return meter cached meter data to ensure meter_id and values are consistent."""
        if not self._meter_cache.get(f"{meter_id}_{self._data_direction}"):
            if self._data_direction:
                self._meter_cache[f"{meter_id}_{self._data_direction}"] = service_meter.get(self._data_direction)
            else:
                self._meter_cache[f"{meter_id}_{self._data_direction}"] = service_meter.get(choice(list(service_meter)))
        return self._meter_cache.get(f"{meter_id}_{self._data_direction}")
