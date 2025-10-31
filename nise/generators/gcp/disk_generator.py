#
# Copyright 2025 Red Hat, Inc.
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
"""Module for gcp persistent disk."""

import uuid
from datetime import datetime
from random import choice
from random import uniform

from nise.generators.gcp.gcp_generator import GCP_REPORT_COLUMNS_JSONL
from nise.generators.gcp.gcp_generator import GCPGenerator
from functools import cached_property
from nise.helpers import gcp_calculate_persistent_disk_usage_amount
from nise.helpers import gcp_calculate_usage_amount_in_pricing


# Persistent Disk sku lists:
# 1. https://cloud.google.com/skus/sku-groups/on-demand-persistent-disk-hdd?hl=en
# 2. https://cloud.google.com/skus/sku-groups/persistent-disk-ssd-storage?hl=en
# 3. https://cloud.google.com/skus/sku-groups/on-demand-persistent-disk-ssd?hl=en
# 4. https://cloud.google.com/skus/sku-groups/on-demand-balanced-persistent-disk?hl=en
# 5. https://cloud.google.com/skus/sku-groups/on-demand-persistent-disk-hdd-capacity?hl=en
# 6. https://cloud.google.com/skus/sku-groups/on-demand-persistent-disk-ssd-in-india?hl=en
# 7. https://cloud.google.com/skus/sku-groups/regional-on-demand-persistent-disk-ssd-doha?hl=en


class PersistentDiskGenerator(GCPGenerator):
    """Generator for GCP persistent disk data."""

    SERVICE = "Compute Engine"  # Service Description and Service ID
    SERVICE_ID = "6F81-5844-456A"

    SKU_DESCRIPTION = {"3C62-891B-C73C": "Regional Storage PD Capacity", "D973-5D65-BAB2": "Storage PD Capacity"}
    USAGE_UNIT = "byte-seconds"
    PRICING_UNIT = "gibibyte month"
    LABELS = (([{"key": "vm_key_proj2", "value": "vm_label_proj2"}]), ([]))
    DEFAULT_CAPACITIES = [30, 60, 100, 10, 20]
    DEFAULT_REGIONS = ["us-central1", "us-west1", "asia-southeast2", "europe-west1"]

    def __init__(self, start_date, end_date, currency, project, attributes=None):  # noqa: C901
        """Initialize the cloud storage generator."""
        super().__init__(start_date, end_date, currency, project, attributes)
        if not self._resource_global_name:
            self._resource_global_name = (
                f"/compute.googleapis.com/projects/{self.project_id}/zones/{self.region}/disk/{self.disk_id}"
            )
        if not self._resource_name:
            self._resource_name = self.fake.word()
        if not self._price:
            self._price = round(uniform(0, 0.01), 7)
        self.validate_attributes()

    def validate_attributes(self):
        unsupported_attributes = ["usage.amount", "usage.amount_in_pricing_units"]
        for attr in unsupported_attributes:
            if self.attributes.get(attr):
                raise ValueError(f"Attribute {attr} is populated through capacity with provisioned disk.")

    @cached_property
    def region(self):
        if region := self.attributes.get("location.region"):
            return region
        if region := self.project.get("region"):
            return region
        return choice(self.DEFAULT_REGIONS)

    @cached_property
    def disk_id(self):
        if disk_id := self.attributes.get("disk_id"):
            return disk_id
        return f"pvc-{uuid.uuid4()}"

    @cached_property
    def capacity(self):
        if capacity := self.attributes.get("capacity"):
            return int(capacity)

        return choice(self.DEFAULT_CAPACITIES)

    @cached_property
    def sku_id(self):
        return self.attributes.get("sku_id", choice(list(self.SKU_DESCRIPTION.keys())))

    @cached_property
    def sku_description(self):
        return self.SKU_DESCRIPTION.get(self.sku_id, choice(list(self.SKU_DESCRIPTION.values())))

    @cached_property
    def usage_amount(self):
        # Added as cached property to avoid recalculating per row
        return gcp_calculate_persistent_disk_usage_amount(self.capacity)

    def _update_data(self, row):  # noqa: C901
        """Update a data row with compute values."""
        usage_date = datetime.strptime(row.get("usage_start_time"), "%Y-%m-%dT%H:%M:%S")
        usage_in_pricing_units = gcp_calculate_usage_amount_in_pricing(usage_date, self.usage_amount)
        cost = usage_in_pricing_units * self._price
        row["service.description"] = self.SERVICE
        row["service.id"] = self.SERVICE_ID
        row["sku.id"] = self.sku_id
        row["sku.description"] = self.sku_description
        row["usage.unit"] = self.USAGE_UNIT
        row["usage.pricing_unit"] = self.PRICING_UNIT
        row["cost_type"] = "regular"
        row["currency_conversion_rate"] = 1
        row["usage.amount"] = self.usage_amount
        row["usage.amount_in_pricing_units"] = usage_in_pricing_units
        row["cost"] = cost
        row["credits"] = self._gen_credit(self._credit_amount)
        row["invoice.month"] = f"{usage_date.year}{usage_date.month:02d}"

        if self.attributes:
            for key in self.attributes:
                if key in self.column_labels:
                    row[key] = self.attributes[key]

        row["currency"] = self._currency
        row["labels"] = self.determine_labels(self.LABELS)
        row["system_labels"] = []
        row["resource.name"] = self._resource_name
        row["resource.global_name"] = self._resource_global_name
        return row

    def generate_data(self, report_type=None):
        """Generate GCP compute data for some days."""
        return self._generate_hourly_data()


class JSONLPersistentDiskGenerator(PersistentDiskGenerator):
    """Generator for GCP Compute Engine data."""

    LABELS = (([{"key": "vm_key_proj2", "value": "vm_label_proj2"}]), ([]))

    def __init__(self, start_date, end_date, currency, project, attributes=None):
        super().__init__(start_date, end_date, currency, project, attributes)
        self.column_labels = GCP_REPORT_COLUMNS_JSONL + ("resource",)
        self.return_list = True
        self._currency = currency

    def _update_data(self, row):  # noqa: C901
        """Update a data row with compute values."""
        usage_date = datetime.strptime(row.get("usage_start_time"), "%Y-%m-%dT%H:%M:%S")
        usage_in_pricing_units = gcp_calculate_usage_amount_in_pricing(usage_date, self.usage_amount)
        cost = usage_in_pricing_units * self._price

        row["service"] = {"description": self.SERVICE, "id": self.SERVICE_ID}
        row["sku"] = {
            "id": self.sku_id,
            "description": self.sku_description,
        }
        row["usage"] = {
            "unit": self.USAGE_UNIT,
            "pricing_unit": self.PRICING_UNIT,
            "amount": self.usage_amount,
            "amount_in_pricing_units": usage_in_pricing_units,
        }
        row["cost"] = cost
        row["credits"] = self._gen_credit(self._credit_amount, json_return=True)
        row["cost_type"] = "regular"
        row["currency_conversion_rate"] = 1
        row["invoice"] = {"month": datetime.strptime(row.get("usage_start_time")[:7], "%Y-%m").strftime("%Y%m")}
        row["resource"] = {"name": self._resource_name, "global_name": self._resource_global_name}
        row["currency"] = self._currency
        row["system_labels"] = []
        if self.attributes:
            for key in self.attributes:
                if key in self.column_labels:
                    row[key] = self.attributes[key]
                elif key.split(".")[0] in self.column_labels:
                    outer_key, inner_key = key.split(".")
                    row[outer_key][inner_key] = self.attributes[key]
        row["labels"] = self.determine_labels(self.LABELS)

        return row

    def generate_data(self, report_type=None):
        """Generate GCP compute data for some days."""
        return self._generate_hourly_data()
