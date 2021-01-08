"""Module for gcp cloud storage data generation."""
# from random import choice
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
        # TODO: Complete the storage generator
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
