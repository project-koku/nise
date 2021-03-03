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
"""Abstract class for gcp data generation."""
import datetime
from abc import abstractmethod
from random import choice
from random import randint
from random import uniform

from nise.generators.generator import AbstractGenerator

GCP_REPORT_COLUMNS = (
    "billing_account_id",
    "service.id",
    "service.description",
    "sku.id",
    "sku.description",
    "usage_start_time",
    "usage_end_time",
    "project.id",
    "project.name",
    "project.labels",
    "project.ancestry_numbers",
    "labels",
    "system_labels",
    "location.location",
    "location.country",
    "location.region",
    "location.zone",
    "export_time",
    "cost",
    "currency",
    "currency_conversion_rate",
    "usage.amount",
    "usage.unit",
    "usage.amount_in_pricing_units",
    "usage.pricing_unit",
    "credits",
    "invoice.month",
    "cost_type",
)

GCP_REPORT_COLUMNS_JSONL = (
    "billing_account_id",
    "service",
    "sku",
    "usage_start_time",
    "usage_end_time",
    "project",
    "labels",
    "system_labels",
    "location",
    "export_time",
    "cost",
    "currency",
    "currency_conversion_rate",
    "usage",
    "credits",
    "invoice",
    "cost_type",
)

GCP_INSTANCE_TYPES = ("e2-medium", "n1-standard-4", "m2-megamem-416", "a2-highgpu-1g")


class GCPGenerator(AbstractGenerator):
    """Abstract class for GCP generators."""

    def __init__(self, start_date, end_date, project, attributes=None):
        """
        Initialize the generator.

        Args:
            start_date (datetime): Day to start generating reports from.
            end_date (datetime): Last day to generate reports for.
            project_id (string): GCP project id

        """
        super().__init__(start_date, end_date)
        self.project = project
        self.num_instances = 1 if attributes else randint(2, 60)
        self.attributes = attributes
        self.column_labels = GCP_REPORT_COLUMNS
        self.return_list = False
        # class vars to be set by the child classes based off attributes.
        self._tags = None
        self._usage_amount = None
        self._pricing_amount = None
        self._price = None
        self._sku = None
        self._instance_type = choice(GCP_INSTANCE_TYPES)
        self._service = None

    @staticmethod
    def _create_days_list(start_date, end_date):
        """Create a list of days given the date range args."""
        days = []

        curr_date = start_date
        while curr_date < end_date:
            day = {"start": curr_date, "end": curr_date + datetime.timedelta(days=1)}
            days.append(day)
            curr_date = curr_date + datetime.timedelta(days=1)

        return days

    @staticmethod
    def timestamp(in_date):
        """Provide timestamp for a date."""
        if not in_date or not isinstance(in_date, datetime.datetime):
            raise ValueError("in_date must be a date object.")
        return in_date.strftime("%Y-%m-%dT%H:%M:%S%z")

    @abstractmethod
    def generate_data(self, report_type=None):
        """Responsible for generating data."""

    def _init_data_row(self, start, end, **kwargs):  # noqa: C901
        """Create a row of data with placeholder for all headers."""
        if not start or not end:
            raise ValueError("start and end must be date objects.")
        if not isinstance(start, datetime.datetime):
            raise ValueError("start must be a date object.")
        if not isinstance(end, datetime.datetime):
            raise ValueError("end must be a date object.")

        row = {}
        # Initialize the start and end time measured
        time_bill_start = start
        time_bill_end = time_bill_start + datetime.timedelta(hours=1)
        for column in self.column_labels:
            row[column] = ""
            if column == "usage_start_time":
                row[column] = GCPGenerator.timestamp(time_bill_start)
            elif column == "usage_end_time":
                row[column] = GCPGenerator.timestamp(time_bill_end)
            elif column == "export_time":
                export_time = time_bill_end + datetime.timedelta(
                    hours=randint(1, 5), minutes=randint(1, 59), seconds=randint(1, 59)
                )
                row[column] = GCPGenerator.timestamp(export_time)
        row.update(self.project)
        return row

    def _gen_usage_unit_amount(self, usage_unit):
        """Generate the correct amount for usage unit."""
        # All upper and lower bound values were estimated for each unit
        if self._usage_amount:
            return self._usage_amount
        if usage_unit == "byte-seconds":
            return self.fake.pyint(min_value=1000, max_value=100000)
        if usage_unit == "bytes":
            return self.fake.pyint(min_value=1000, max_value=10000000)
        if usage_unit == "seconds":
            return self.fake.pyfloat(max_value=3600, positive=True)
        return 0

    def _gen_pricing_unit_amount(self, pricing_unit, amount):
        """Generate the correct amount in pricing units."""
        if self._pricing_amount:
            return self._pricing_amount
        if pricing_unit == "gibibyte month":
            return amount * 0.00244752
        if pricing_unit == "gibibyte hour":
            return amount * (3.3528 * 10 ** -6)
        if pricing_unit == "gibibyte":
            return amount * (9.31323 * 10 ** -0)
        if pricing_unit == "hour":
            return amount / 3600.00
        return 0

    def _gen_cost(self, pricing_amount):
        """Generate the cost based off the pricing amount."""
        if self._price:
            return pricing_amount * self._price
        else:
            return round(uniform(0, 0.01), 7)

    def determine_system_labels(self, pricing_unit):
        """Determine the system labels if instance-type exists."""
        # We only want to set the instance-type if the pricing unit is hourly.
        if pricing_unit != "hour":
            if self.return_list:
                return []
            return "[]"
        system_label_format = [
            {"key": "compute.googleapis.com/cores", "value": "2"},
            {"key": "compute.googleapis.com/machine_spec", "value": self._instance_type},
            {"key": "compute.googleapis.com/memory", "value": "4096"},
        ]
        if self.return_list:
            return system_label_format
        else:
            return str(system_label_format)

    def determine_labels(self, labels):
        """Determine the labels based on tags param."""
        if not self._tags:
            return choice(labels)
        label_format = []
        for tag_key, tag_val in self._tags.items():
            dict_format = {"key": tag_key, "value": tag_val}
            label_format.append(dict_format)
        if self.return_list:
            return label_format
        else:
            return str(label_format)

    def _add_common_usage_info(self, row, start, end, **kwargs):
        """Not needed for GCP."""

    @abstractmethod
    def _update_data(self, row, start, end, **kwargs):
        """Update a data row."""

    def _generate_hourly_data(self, **kwargs):
        """Not needed for GCP."""
        for hour in self.hours:
            start = hour.get("start")
            end = hour.get("end")
            row = self._init_data_row(start, end)
            row = self._update_data(row)
            yield row
