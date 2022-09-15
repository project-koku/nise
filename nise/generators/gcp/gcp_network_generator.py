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

from nise.generators.gcp.gcp_generator import GCP_REPORT_COLUMNS_JSONL
from nise.generators.gcp.gcp_generator import GCPGenerator


class GCPNetworkGenerator(GCPGenerator):
    """Generator for GCP Network data."""

    # Service Description and Service ID
    SERVICE = (
        ("Network", "12B3-1234-JK3C"),
        ("VPC", "23C3-JS3K-SDL3"),
        ("Firewall", "LSKD-23RD-23RS"),
        ("Route", "2NF2-342K-SD3C"),
        ("IP", "23KD-SL3N-SLK3"),
        ("Cloud DNS", "8C22-6FC3-D478"),  # Real service id
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

    LABELS = (([{"key": "vm_key_proj2", "value": "vm_label_proj2"}]), ([]))

    def __init__(self, start_date, end_date, currency, project, attributes=None):  # noqa: C901
        """Initialize the cloud storage generator."""
        super().__init__(start_date, end_date, currency, project, attributes)
        self.credit_total = 0
        self._currency = currency
        if self.attributes:
            if self.attributes.get("labels"):
                self._labels = self.attributes.get("labels")
            if self.attributes.get("usage.amount"):
                self._usage_amount = self.attributes.get("usage.amount")
            if self.attributes.get("usage.amount_in_pricing_units"):
                self._pricing_amount = self.attributes.get("usage.amount_in_pricing_units")
            if self.attributes.get("price"):
                self._price = self.attributes.get("price")
            if self.attributes.get("service.description"):
                for service in self.SERVICE:
                    if self.attributes.get("service.description").lower() == service[0].lower():
                        self._service = service
            if self.attributes.get("credit_amount"):
                self._credit_amount = self.attributes.get("credit_amount")
            if self.attributes.get("resource.name"):
                self._resource_name = self.attributes.get("resource.name")
            if self.attributes.get("resource.global_name"):
                self._resource_global_name = self.attributes.get("resource.global_name")

    def _update_data(self, row):  # noqa: C901
        """Update a data row with compute values."""
        service = choice(self.SERVICE)
        if self._service:
            service = self._service
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
        row["cost_type"] = "regular"
        row["currency_conversion_rate"] = 1
        row["usage.amount"] = self._gen_usage_unit_amount(usage_unit)
        row["usage.amount_in_pricing_units"] = self._gen_pricing_unit_amount(pricing_unit, row["usage.amount"])
        cost = self._gen_cost(row["usage.amount_in_pricing_units"])
        row["cost"] = cost
        credit, credit_total = self._gen_credit(self.credit_total, self._credit_amount)
        self.credit_total = credit_total
        row["credits"] = credit
        usage_date = datetime.strptime(row.get("usage_start_time"), "%Y-%m-%dT%H:%M:%S")
        row["invoice.month"] = f"{usage_date.year}{usage_date.month:02d}"

        if self.attributes:
            for key in self.attributes:
                if key in self.column_labels:
                    row[key] = self.attributes[key]

        row["currency"] = self._currency
        row["labels"] = self.determine_labels(self.LABELS)
        if self.resource_level:
            resource = self._generate_resource(
                self._resource_name, self._resource_global_name, self.project.get("region")
            )
            row["resource.name"] = resource.get("name")
            row["resource.global_name"] = resource.get("global_name")

        return row

    def generate_data(self, report_type=None):
        """Generate GCP compute data for some days."""
        return self._generate_hourly_data()


class JSONLGCPNetworkGenerator(GCPNetworkGenerator):
    """Generator for GCP Database data."""

    LABELS = (([{"key": "vm_key_proj2", "value": "vm_label_proj2"}]), ([]))

    def __init__(self, start_date, end_date, currency, project, attributes=None):
        super().__init__(start_date, end_date, currency, project, attributes)
        self.column_labels = (
            GCP_REPORT_COLUMNS_JSONL + ("resource",) if self.resource_level else GCP_REPORT_COLUMNS_JSONL
        )
        self.return_list = True

    def _update_data(self, row):  # noqa: C901
        """Update a data row with compute values."""
        service_choice = choice(self.SERVICE)
        if self._service:
            service_choice = self._service
        sku_choice = choice(self.SKU)
        row["system_labels"] = []
        service = {}
        service["description"] = service_choice[0]
        service["id"] = service_choice[1]
        row["service"] = service
        sku = {}
        sku["id"] = sku_choice[0]
        sku["description"] = sku_choice[1]
        row["sku"] = sku
        usage_unit = sku_choice[2]
        pricing_unit = sku_choice[3]
        usage = {}
        usage["unit"] = usage_unit
        usage["pricing_unit"] = pricing_unit
        row["cost_type"] = "regular"
        row["currency_conversion_rate"] = 1
        usage["amount"] = self._gen_usage_unit_amount(usage_unit)
        usage["amount_in_pricing_units"] = self._gen_pricing_unit_amount(pricing_unit, usage["amount"])
        cost = self._gen_cost(usage["amount_in_pricing_units"])
        row["cost"] = cost
        row["usage"] = usage
        credit, credit_total = self._gen_credit(self.credit_total, self._credit_amount, True)
        self.credit_total = credit_total
        row["credits"] = credit
        usage_date = datetime.strptime(row.get("usage_start_time"), "%Y-%m-%dT%H:%M:%S")
        invoice = {}
        usage_date = datetime.strptime(row.get("usage_start_time"), "%Y-%m-%dT%H:%M:%S")
        invoice["month"] = f"{usage_date.year}{usage_date.month:02d}"
        row["invoice"] = invoice
        if self.resource_level:
            resource = self._generate_resource()
            row["resource"] = resource

        if self.attributes:
            for key in self.attributes:
                if key in self.column_labels:
                    row[key] = self.attributes[key]
                elif key.split(".")[0] in self.column_labels:
                    outer_key, inner_key = key.split(".")
                    row[outer_key][inner_key] = self.attributes[key]

        row["currency"] = self._currency
        row["labels"] = self.determine_labels(self.LABELS)

        return row

    def generate_data(self, report_type=None):
        """Generate GCP compute data for some days."""
        return self._generate_hourly_data()
