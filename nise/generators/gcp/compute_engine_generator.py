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
"""Module for gcp compute engine data generation."""
from datetime import datetime
from random import choice
from random import uniform

from nise.generators.gcp.gcp_generator import GCP_REPORT_COLUMNS_JSONL
from nise.generators.gcp.gcp_generator import GCPGenerator


class ComputeEngineGenerator(GCPGenerator):
    """Generator for GCP Compute Engine data."""

    SERVICE = ("Compute Engine", "6F81-5844-456A")  # Service Description and Service ID

    SKU = (  # (ID, Description, Usage Unit, Pricing Unit)
        ("D973-5D65-BAB2", "Storage PD Capacity", "byte-seconds", "gibibyte month"),
        ("D0CC-50DF-59D2", "Network Inter Zone Ingress", "bytes", "gibibyte"),
        ("F449-33EC-A5EF", "E2 Instance Ram running in Americas", "byte-seconds", "gibibyte hour"),
        ("C054-7F72-A02E", "External IP Charge on a Standard VM", "seconds", "hour"),
        ("CF4E-A0C7-E3BF", "E2 Instance Core running in Americas", "seconds", "hour"),
        ("C0CF-3E3B-57FB", "Licensing Fee for Debian 10 Buster (CPU cost)", "seconds", "hour"),
        ("0C5C-D8E4-38C1", "Licensing Fee for Debian 10 Buster (CPU cost)", "seconds", "hour"),
        ("CD20-B4CA-0F7C", "Licensing Fee for Debian 10 Buster (RAM cost)", "byte-seconds", "gibiyte hour"),
        ("6B8F-E63D-832B", "Network Internet Egress from Americas to APAC", "bytes", "gibibyte"),
        ("DFA5-B5C6-36D6", "Network Internet Egress from Americas to EMEA", "bytes", "gibibyte"),
        ("9DE9-9092-B3BC", "Network Internet Egress from Americas to China", "bytes", "gibibyte"),
        ("7151-106A-2684", "Network Internet Ingress from APAC to Americas", "bytes", "gibibyte"),
        ("2F99-3A90-373B", "Network Internet Ingress from EMEA to Americas", "bytes", "gibibyte"),
        ("92CB-C25F-B1D1", "Network Google Egress from Americas to Americas", "bytes", "gibibyte"),
        ("227B-5B2B-A75A", "Network Internet Ingress from China to Americas", "bytes", "gibibyte"),
        ("123C-0EFC-B7C8", "Network Google Ingress from Americas to Americas", "bytes", "gibibyte"),
        ("F274-1692-F213", "Network Internet Engress from Americas to Americas", "bytes", "gibibyte"),
        ("92CB-C25F-B1D1", "Network Google Egress from Americas to Americas", "bytes", "gibibyte"),  # Left off at 125
    )

    LABELS = (("[{'key': 'vm_key_proj2', 'value': 'vm_label_proj2'}]"), ("[]"))

    SYSTEM_LABELS = (
        (
            """[{'key': 'compute.googleapis.com/cores', 'value': '2'}, {'key': 'compute.googleapis.com/machine_spec', 'value': 'e2-medium'}, {'key': 'compute.googleapis.com/memory', 'value': '4096'}]"""  # noqa: E501
        ),
        ("[]"),
    )

    def _update_data(self, row):  # noqa: C901
        """Update a data row with compute values."""
        sku = choice(self.SKU)
        row["service.description"] = self.SERVICE[0]
        row["service.id"] = self.SERVICE[1]
        row["sku.id"] = sku[0]
        row["sku.description"] = sku[1]
        row["cost"] = round(uniform(0, 0.01), 7)
        usage_unit = sku[2]
        pricing_unit = sku[3]
        row["usage.unit"] = usage_unit
        row["usage.pricing_unit"] = pricing_unit
        row["labels"] = choice(self.LABELS)
        row["system_labels"] = choice(self.SYSTEM_LABELS)
        row["usage.amount"] = 0

        # All upper and lower bound values were estimated for each unit
        if usage_unit == "byte-seconds":
            amount = self.fake.pyint(min_value=1000, max_value=100000)
            row["usage.amount"] = amount
            if pricing_unit == "gibibyte month":
                row["usage.amount_in_pricing_units"] = amount * 0.00244752
            elif pricing_unit == "gibibyte hour":
                row["usage.amount_in_pricing_units"] = amount * (3.3528 * 10 ** -6)
        elif usage_unit == "bytes":
            amount = self.fake.pyint(min_value=1000, max_value=10000000)
            row["usage.amount"] = amount
            if pricing_unit == "gibibyte":
                row["usage.amount_in_pricing_units"] = amount * (9.31323 * 10 ** -0)
        elif usage_unit == "seconds":
            amount = self.fake.pyfloat(max_value=3600, positive=True)
            row["usage.amount"] = amount
            if pricing_unit == "hour":
                row["usage.amount_in_pricing_units"] = amount / 3600.00

        row["credits"] = "[]"
        row["cost_type"] = "regular"
        row["currency"] = "USD"
        row["currency_conversion_rate"] = 1
        row["invoice.month"] = f"{self.start_date.year}{self.start_date.month}"

        if self.attributes:
            for key in self.attributes:
                if key in self.column_labels:
                    row[key] = self.attributes[key]
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


class JSONLComputeEngineGenerator(ComputeEngineGenerator):
    """Generator for GCP Compute Engine data."""

    LABELS = (([{"key": "vm_key_proj2", "value": "vm_label_proj2"}]), ([]))

    SYSTEM_LABELS = (
        (
            [
                {"key": "compute.googleapis.com/cores", "value": "2"},
                {"key": "compute.googleapis.com/machine_spec", "value": "e2-medium"},
                {"key": "compute.googleapis.com/memory", "value": "4096"},
            ]
        ),
        ([]),
    )

    def __init__(self, start_date, end_date, project, attributes=None):
        super().__init__(start_date, end_date, project, attributes)
        self.column_labels = GCP_REPORT_COLUMNS_JSONL

    def _update_data(self, row):  # noqa: C901
        """Update a data row with compute values."""
        sku_choice = choice(self.SKU)
        service = {}
        service["description"] = self.SERVICE[0]
        service["id"] = self.SERVICE[1]
        row["service"] = service
        sku = {}
        sku["id"] = sku_choice[0]
        sku["description"] = sku_choice[1]
        row["sku"] = sku
        row["cost"] = round(uniform(0, 0.01), 7)
        usage_unit = sku_choice[2]
        pricing_unit = sku_choice[3]
        usage = {}
        usage["unit"] = usage_unit
        usage["pricing_unit"] = pricing_unit
        row["labels"] = choice(self.LABELS)
        row["system_labels"] = choice(self.SYSTEM_LABELS)
        usage["amount"] = 0

        # All upper and lower bound values were estimated for each unit
        if usage_unit == "byte-seconds":
            amount = self.fake.pyint(min_value=1000, max_value=100000)
            usage["amount"] = amount
            if pricing_unit == "gibibyte month":
                usage["amount_in_pricing_units"] = amount * 0.00244752
            elif pricing_unit == "gibibyte hour":
                usage["amount_in_pricing_units"] = amount * (3.3528 * 10 ** -6)
        elif usage_unit == "bytes":
            amount = self.fake.pyint(min_value=1000, max_value=10000000)
            usage["amount"] = amount
            if pricing_unit == "gibibyte":
                usage["amount_in_pricing_units"] = amount * (9.31323 * 10 ** -0)
        elif usage_unit == "seconds":
            amount = self.fake.pyfloat(max_value=3600, positive=True)
            usage["amount"] = amount
            if pricing_unit == "hour":
                usage["amount_in_pricing_units"] = amount / 3600.00

        row["usage"] = usage
        row["credits"] = {}
        row["cost_type"] = "regular"
        row["currency"] = "USD"
        row["currency_conversion_rate"] = 1
        invoice = {}
        year = datetime.strptime(row.get("usage_start_time"), "%Y-%m-%dT%H:%M:%S").year
        month = datetime.strptime(row.get("usage_start_time"), "%Y-%m-%dT%H:%M:%S").month
        invoice["month"] = f"{year}{month:02d}"
        row["invoice"] = invoice

        if self.attributes:
            for key in self.attributes:
                if key in self.column_labels:
                    row[key] = self.attributes[key]
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
