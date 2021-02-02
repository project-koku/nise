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
"""Generator for GCP storage cost."""
from random import choice
from random import randint
from random import uniform

from nise.generators.gcp.gcp_generator import GCPGenerator


class CloudStorageGenerator(GCPGenerator):
    """Generator for GCP Cloud Storage data."""

    # Other possible services for storage, but we need examples
    # to know the usage unit and pricing unit
    #  "Filestore", "zzzz-1234-1993")
    #  "Storage", "blah-zxzx-3234")
    SERVICES = (("Cloud Storage", "95FF-2EF5-5EA1"),)

    SKU_MAPPING = {
        "Cloud Storage": (  # (ID, Description, Usage Unit, Pricing Unit)
            ("E5F0-6A5D-7BAD", "Standard Storage US Regional", "byte-seconds", "gibibyte month"),
        )
    }

    LABELS = (("[{'key': 'test_storage_key', 'value': 'test_storage_label'}]"), ("[]"))

    SYSTEM_LABELS = (("[]"),)

    def _update_data(self, row):  # noqa: C901
        """Update a data row with compute values."""
        service = choice(self.SERVICES)
        sku_options = self.SKU_MAPPING[service[0]]
        sku = choice(sku_options)
        row["service.description"] = service[0]
        row["service.id"] = service[1]
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
        if usage_unit == "bytes":
            amount = self.fake.pyint(min_value=1000, max_value=10000000)
            row["usage.amount"] = amount
            if pricing_unit == "gibibyte":
                row["usage.amount_in_pricing_units"] = amount * (9.31323 * 10 ** -0)
        elif usage_unit == "requests":
            amount = randint(0, 10)
            row["usage.amount"] = amount
            row["usage.amount_in_pricing_units"] = amount

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
            row = self._init_data_row(day["start"], day["end"])
            row = self._update_data(row)
            rows.append(row)
            data[day["start"]] = rows
        return data
