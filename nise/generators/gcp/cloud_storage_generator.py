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
"""Module for gcp cloud storage data generation."""
from random import choice
from random import randint

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

    def __init__(self, start_date, end_date, project, user_config=None):
        """Initialize the generator."""
        # pass defaults to the template.
        num_instances = randint(2, 10)
        self.TEMPLATE_KWARGS["cloudstorage_gens"] = []
        for _ in range(0, num_instances):
            self.TEMPLATE_KWARGS["cloudstorage_gens"].append({"_storage": choice(self.STORAGE)})

        super().__init__(start_date, end_date, project, user_config=user_config)

    def _update_data(self, row, config={}):
        """Update a data row with storage values."""
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
        """Generate GCP storage data for some days."""
        days = self._create_days_list(self.start_date, self.end_date)
        data = {}
        for day in days:
            rows = []
            for config in self.config:
                row = self._init_data_row(day["start"], day["end"])
                row = self._update_data(row, config=config)
                rows.append(row)
            data[day["start"]] = rows
        return data
