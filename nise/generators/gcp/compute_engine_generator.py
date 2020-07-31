#
# Copyright 2019 Red Hat, Inc.
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
"""Module for gcp compute engine data generation."""
from random import choice
from random import randint

from nise.generators.gcp.gcp_generator import GCPGenerator


class ComputeEngineGenerator(GCPGenerator):
    """Generator for GCP Compute Engine data."""

    COMPUTE = (
        (
            "com.google.cloud/services/compute-engine/Licensed1000201CoreRange_1_OrMore",
            "seconds",
            "Licensing Fee for Ubuntu 16.04 (Xenial Xerus) running on Instance Core",
        ),
        (
            "com.google.cloud/services/compute-engine/Licensed1000201Ram",
            "byte-seconds",
            "Licensing Fee for Ubuntu 16.04 (Xenial Xerus) running on Instance Ram",
        ),
        (
            "com.google.cloud/services/compute-engine/Licensed1000207Core",
            "seconds",
            "Licensing Fee for CentOS 7 running on Instance Core",
        ),
        (
            "com.google.cloud/services/compute-engine/Licensed1000207G1Small",
            "seconds",
            "Licensing Fee for CentOS 7 running on Small instance with 1 VCPU",
        ),
        (
            "com.google.cloud/services/compute-engine/Licensed1000207Ram",
            "byte-seconds",
            "Licensing Fee for CentOS 7 running on Instance Ram",
        ),
        (
            "com.google.cloud/services/compute-engine/NetworkHttpProxyIngress",
            "bytes",
            "Network HTTP Load Balancing Ingress from Load Balancer",
        ),
        ("com.google.cloud/services/compute-engine/StoragePdCapacity", "byte-seconds", "Storage PD Capacity"),
        (
            "com.google.cloud/services/compute-engine/VmimageN1StandardCore",
            "seconds",
            "N1 Predefined Instance Core running in Americas",
        ),
        (
            "com.google.cloud/services/compute-engine/VmimageN1StandardRam",
            "byte-seconds",
            "N1 Predefined Instance Ram running in Americas",
        ),
    )

    def __init__(self, start_date, end_date, project, user_config=None):
        """Initialize the generator."""
        # pass defaults to the template.
        num_instances = randint(2, 10)
        self.TEMPLATE_KWARGS["computeengine_gens"] = []
        for _ in range(0, num_instances):
            self.TEMPLATE_KWARGS["computeengine_gens"].append({"_compute": choice(self.COMPUTE)})

        super().__init__(start_date, end_date, project, user_config=user_config)

    def _update_data(self, row, config={}):
        """Update a data row with compute values."""
        row["Line Item"] = config.get("Line Item")
        row["Measurement1"] = config.get("Measurement1")
        row["Measurement1 Total Consumption"] = config.get("Measurement1 Total Consumption")
        row["Measurement1 Units"] = config.get("Measurement1 Units")
        row["Cost"] = config.get("Cost")
        row["Currency"] = config.get("Currency")
        row["Description"] = config.get("Description")
        row["Credit1"] = config.get("Credit1")
        row["Credit1 Amount"] = config.get("Credit1 Amount")
        row["Credit1 Currency"] = config.get("Credit1 Currency")
        return row

    def generate_data(self, report_type=None):
        """Generate GCP compute data for some days."""
        days = self._create_days_list(self.start_date, self.end_date)
        data = {}
        for day in days:
            rows = []
            for config in self.config:
                row = self._init_data_row(day["start"], day["end"])
                row = self._update_data(row, config)
                rows.append(row)
            data[day["start"]] = rows
        return data
