#
# Copyright 2021 Red Hat, Inc.
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
"""Module for gcp network data generation."""
from datetime import datetime
from random import choice
from random import uniform

from nise.generators.gcp.gcp_generator import GCPGenerator

# from nise.generators.gcp.gcp_generator import GCP_REPORT_COLUMNS_JSONL


class GCPNetworkGenerator(GCPGenerator):
    """Generator for GCP Network data."""

    # Service Description and Service ID
    SERVICE = (
        ("Network", "12B3-1234-JK3C"),
        ("VPC", "23C3-JS3K-SDL3"),
        ("Firewall", "LSKD-23RD-23RS"),
        ("Route", "2NF2-342K-SD3C"),
        ("IP", "23KD-SL3N-SLK3"),
        ("DNS", "8C22-6FC3-D478"),  # Real service id
        ("CDN", "SWL2-234S-DK2D"),
        ("NAT", "SL2D-SLJ3-IYV3"),
        ("Traffic Director", "SL2C-FNMW-3CI2"),
        ("Service Discovery", "23NS-FNA3-GM3C"),
        ("Cloud Domains", "2J34-SM34-SMD3"),
        ("Private Service Connect", "JFJH-34J3-SM5D"),
        ("Cloud Armor", "234L-FJ56-SJ35"),
    )

    # (ID, Description, Usage Unit, Pricing Unit)
    SKU = (("8C22-6FC3-D478", "ManagedZone", "seconds", "month"),)

    LABELS = (("[{'key': 'vm_key_proj2', 'value': 'vm_label_proj2'}]"), ("[]"))

    def _update_data(self, row):  # noqa: C901
        """Update a data row with compute values."""

        service = choice(self.SERVICE)
        sku = choice(self.SKU)
        row["system_labels"] = "[]"
        row["service.description"] = service[0]
        row["service.id"] = service[1]
        row["sku.id"] = sku[0]
        row["sku.description"] = sku[1]
        usage_unit = sku[2]
        pricing_unit = sku[3]
        row["usage.unit"] = usage_unit
        row["usage.pricing_unit"] = pricing_unit
        row["labels"] = choice(self.LABELS)
        row["credits"] = "[]"
        row["cost_type"] = "regular"
        row["currency"] = "USD"
        row["currency_conversion_rate"] = 1
        if self.attributes and self.attributes.get("usage.amount"):
            row["usage.amount"] = self.attributes.get("usage.amount")
        else:
            row["usage.amount"] = self._gen_usage_unit_amount(usage_unit)
        if self.attributes and self.attributes.get("usage.amount_in_pricing_units"):
            row["usage.amount_in_pricing_units"] = self.attributes.get("usage.amount_in_pricing_units")
        else:
            row["usage.amount_in_pricing_units"] = self._gen_pricing_unit_amount(pricing_unit, row["usage.amount"])
        if self.attributes and self.attributes.get("price"):
            row["cost"] = row["usage.amount_in_pricing_units"] * self.attributes.get("price")
        else:
            row["cost"] = round(uniform(0, 0.01), 7)
        usage_date = datetime.strptime(row.get("usage_start_time"), "%Y-%m-%dT%H:%M:%S")
        row["invoice.month"] = f"{usage_date.year}{usage_date.month:02d}"
        if self.attributes:
            for key in self.attributes:
                if key in self.column_labels:
                    row[key] = self.attributes[key]
        return row

    def generate_data(self, report_type=None):
        """Generate GCP compute data for some days."""
        return self._generate_hourly_data()
