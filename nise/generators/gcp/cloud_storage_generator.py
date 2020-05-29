"""Module for gcp cloud storage data generation."""
from random import choice

from nise.generators.gcp.gcp_generator import GCPGenerator


class CloudStorageGenerator(GCPGenerator):
    """Generator for GCP Cloud Storage data."""

    STORAGE = (
        ("com.google.cloud/services/cloud-storage/StorageRegionalUsGbsec", "byte-seconds", "Regional Storage US"),
        (
            "com.google.cloud/services/cloud-storage/ClassARequestRegional",
            "byte-seconds",
            "Class A Request Regional Storage",
        ),
        (
            "com.google.cloud/services/cloud-storage/ClassBRequestRegional",
            "byte-seconds",
            "Class B Request Regional Storage",
        ),
        (
            "com.google.cloud/services/cloud-storage/BandwidthDownloadAmerica",
            "bytes",
            "Download Worldwide Destinations (excluding Asia & Australia)",
        ),
    )

    def _update_data(self, row):
        """Update a data row with storage values."""
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
            storage = choice(self.STORAGE)
            row["Line Item"] = storage[0]
            row["Measurement1"] = storage[0]
            row["Measurement1 Total Consumption"] = self.fake.pyint()
            row["Measurement1 Units"] = storage[1]
            row["Cost"] = self.fake.pyint()
            row["Currency"] = "USD"
            row["Description"] = storage[2]
        return row

    def generate_data(self, report_type=None):
        """Generate GCP storage data for some days."""
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
