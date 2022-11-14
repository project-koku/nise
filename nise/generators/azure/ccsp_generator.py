#
# Copyright 2022 Red Hat, Inc.
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
from nise.generators.azure.virtual_machine_generator import VMGenerator


class CCSPGenerator(VMGenerator):
    """Generator for CCSP data."""

    SERVICE_METER = (("Red Hat Enterprise Linux", "Red Hat Enterprise Linux", "1 vCPU VM License", "1 Hour"),)
    SERVICE_INFO_2 = ("Red Hat",)
    ADDITIONAL_INFO = (
        {
            "UsageType": "ComputeHR",
            "ImageType": "Red Hat",
            "ServiceType": "Standard_B1ls",
            "VMName": None,
            "VMProperties": None,
            "VCPUs": 1,
        },
    )
