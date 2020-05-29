"""Module for gcp compute engine data generation."""
from random import choice

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

    def _update_data(self, row):
        """Update a data row with compute values."""
        if self.attributes:
            row["Line Item"] = self.attributes["Line Item"]
            row["Measurement1"] = self.attributes["Measurement1"]
            row["Measurement1 Total Consumption"] = self.attributes["Measurement1 Total Consumption"]
            row["Measurement1 Units"] = self.attributes["Measurement1 Units"]
            row["Cost"] = self.attributes["Cost"]
            row["Currency"] = self.attributes["Currency"]
            row["Description"] = self.attributes["Description"]
            row["Credit1"] = self.attributes["Credit1"]
            row["Credit1 Amount"] = self.attributes["Credit1 Amount"]
            row["Credit1 Currency"] = self.attributes["Credit1 Currency"]

        else:
            compute = choice(self.COMPUTE)
            row["Line Item"] = compute[0]
            row["Measurement1"] = compute[0]
            row["Measurement1 Total Consumption"] = self.fake.pyint()
            row["Measurement1 Units"] = compute[1]
            row["Cost"] = self.fake.pyint()
            row["Currency"] = "USD"
            row["Description"] = compute[2]
        return row

    def generate_data(self, report_type=None):
        """Generate GCP compute data for some days."""
        days = self._create_days_list(self.start_date, self.end_date)
        data = {}
        for day in days:
            rows = []
            for _ in range(self.num_instances):
                row = self._init_data_row(day["start"], day["end"])
                row = self._update_data(row)
                rows.append(row)
            data[day["start"]] = rows
        return data
