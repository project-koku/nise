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
import json
import string
from abc import abstractmethod
from dateutil.relativedelta import relativedelta
from random import choice
from random import randint
from random import uniform
import calendar
from nise.util.constants import SECONDS_IN_HOUR

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
    "partition_date",
)

GCP_RESOURCE_COLUMNS = ("resource.name", "resource.global_name")

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


def apply_different_invoice_month(row, invoice_shift):
    """
    Adjusts the invoice month of a data row by a given month shift.

    This function handles two possible data structures for the invoice month:
    1. A flat key: `{"invoice.month": "202509", ...}`
    2. A nested dictionary: `{"invoice": {"month": "202509"}, ...}`

    It creates a copy of the row, finds the month, applies the shift, and
    updates the row while preserving the original structure.

    Args:
        row (dict): The data row containing invoice information.
        invoice_shift (int): The number of months to shift. Can be positive
                             (for future months) or negative (for past months).

    Returns:
        dict: A new dictionary with the adjusted invoice month. If the invoice
              month cannot be found or is malformed, it returns an unmodified
              copy of the original row.
    """
    new_row = row.copy()
    if invoice_month := new_row.get("invoice.month"):
        invoice_month_date_object = datetime.datetime.strptime(invoice_month, "%Y%m")
    elif invoice_dict := new_row.get("invoice"):
        invoice_month_date_object = datetime.datetime.strptime(invoice_dict["month"], "%Y%m")
    else:
        return new_row

    adjusted_date = invoice_month_date_object + relativedelta(months=invoice_shift)
    adjusted_month = adjusted_date.strftime("%Y%m")
    if "invoice.month" in new_row:
        new_row["invoice.month"] = adjusted_month
    elif "invoice" in new_row:
        new_row["invoice"] = {"month": adjusted_month}
    return new_row


def get_months_in_range(start_date, end_date):
    """
    Generates a list of all months between a start and end date, inclusive.
    """

    months = []
    current_date = start_date.date().replace(day=1)
    end_month_start = end_date.date().replace(day=1)

    while current_date <= end_month_start:
        months.append(current_date)
        current_date += relativedelta(months=1)

    return months


class GCPGenerator(AbstractGenerator):
    """Abstract class for GCP generators."""

    def __init__(self, start_date, end_date, currency, project, attributes=None):
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
        self.attributes = attributes or {}
        self.resource_level = self.attributes.get("resource_level", False)
        self.column_labels = GCP_REPORT_COLUMNS + GCP_RESOURCE_COLUMNS if self.resource_level else GCP_REPORT_COLUMNS
        self.return_list = False
        self._usage_amount = self.attributes.get("usage.amount")
        self._labels = self.attributes.get("labels")
        self._pricing_amount = self.attributes.get("usage.amount_in_pricing_units")
        self._price = self.attributes.get("price")
        self._credit_amount = self.attributes.get("credit_amount")
        self._resource_name = self.attributes.get("resource.name")
        self._resource_global_name = self.attributes.get("resource.global_name")
        self._service = self.attributes.get("service.description")
        self._cross_over_metadata = self.attributes.get("cross_over", {})
        self._instance_type = self.attributes.get("instance_type", choice(GCP_INSTANCE_TYPES))
        self._currency = self.attributes.get("currency", currency)
        self._sku = None

    @property
    def project_id(self):
        if proj_id := self.project.get("project.id"):
            return proj_id
        if proj_id := self.project.get("id"):
            return proj_id

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
        # can't use tz info - local reports doesn't work with "UTC",
        # BigQuery doesn't support UTC offset in the form of +HHMM
        return in_date.strftime("%Y-%m-%dT%H:%M:%S")

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
            elif column == "partition_date":
                row[column] = time_bill_start.strftime("%Y-%m-%d")
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
            return self.fake.pyfloat(max_value=SECONDS_IN_HOUR, positive=True)
        return 0

    def _gen_pricing_unit_amount(self, pricing_unit, amount):
        """Generate the correct amount in pricing units."""
        if self._pricing_amount:
            return self._pricing_amount
        if pricing_unit == "gibibyte month":
            return amount * 0.00244752
        if pricing_unit == "gibibyte hour":
            return amount * (3.3528 * 10**-6)
        if pricing_unit == "gibibyte":
            return amount * (9.31323 * 10**-0)
        if pricing_unit == "hour":
            return amount / SECONDS_IN_HOUR
        return 0

    def _gen_cost(self, pricing_amount):
        """Generate the cost based off the pricing amount."""
        if self._price:
            return pricing_amount * self._price
        else:
            return round(uniform(0, 0.01), 7)

    def _gen_credit(self, credit_amount, json_return=False):
        """Generate the credit dict based off the hourly credit_amount."""
        if json_return:
            default_dict = {"name": "", "amount": 0, "full_name": "", "id": "", "type": ""}
            empty_return = default_dict
        else:
            empty_return = "[]"
        if not credit_amount:
            return empty_return
        else:
            credit_name = "FreeTrial"
            credit_dict = {
                "name": credit_name,
                "amount": credit_amount,
                "full_name": "",
                "id": credit_name,
                "type": "PROMOTION",
            }

            if json_return:
                return credit_dict
            else:
                return str([credit_dict])

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
            return json.dumps(system_label_format)

    def determine_labels(self, labels):
        """Determine the labels based on tags param."""
        if not self._labels:
            if self.return_list:
                return choice(labels)
            else:
                return json.dumps(choice(labels))
        label_format = []
        for label in self._labels:
            if "key" not in label and "value" not in label:
                for tag_key, tag_val in label.items():
                    dict_format = {"key": tag_key, "value": tag_val}
                    label_format.append(dict_format)
            else:
                label_format.append(label)
        if self.return_list:
            return label_format
        else:
            return json.dumps(label_format)

    def _generate_resource(self, region=None):
        name = self._resource_name
        global_name = self._resource_global_name
        if not self._resource_name:
            name = self.fake.word()
            name = f"projects/{self.project_id}/instances/{name}"
        if not self._resource_global_name:
            id = "".join([choice(string.digits) for _ in range(19)])
            global_name = f"//compute.googleapis.com/projects/{self.project_id}/zones/{region}/instances/{id}"
        return {"name": name, "global_name": global_name}

    def _add_common_usage_info(self, row, start, end, **kwargs):
        """Not needed for GCP."""

    @abstractmethod
    def _update_data(self, row, start, end, **kwargs):
        """Update a data row."""

    def _is_invoice_shift_applicable_to_month(self, month_to_check_start):
        """
        Determines if the cross-over logic applies to a specific month.

        Args:
            month_to_check_start (datetime.date): The first day of the month to check.

        Returns:
            bool: True if the invoice shift logic should be applied, False otherwise.
        """
        now = datetime.datetime.now(datetime.UTC)
        month_setting = self._cross_over_metadata.get("month", "all")

        if month_setting == "current":
            current_month_start = now.date().replace(day=1)
            is_applicable_this_month = month_to_check_start == current_month_start
        elif month_setting == "previous":
            previous_month_start = (now - relativedelta(months=1)).date().replace(day=1)
            is_applicable_this_month = month_to_check_start == previous_month_start
        else:
            is_applicable_this_month = True
        return is_applicable_this_month

    def _get_day_to_shift_map(self, cross_over_day_specifiers, start_dt, end_dt):
        """
        Calculates the map of days to invoice shifts based on cross-over settings.
        """
        day_to_shift_map = {}
        if not cross_over_day_specifiers:
            return day_to_shift_map

        # Get list of all months generated in current batch
        months_in_data = get_months_in_range(start_dt, end_dt)

        # Check which of those months the invoice shift is applicable to
        months_to_shift = [month for month in months_in_data if self._is_invoice_shift_applicable_to_month(month)]

        # Build a mapping of {month: {day_of_month: invoice_month_shift}}
        for month in months_to_shift:
            month_key = month.month
            day_to_shift_map[month_key] = {}
            _, num_days_in_month = calendar.monthrange(month.year, month_key)

            # A shift of -1 moves the cost to the previous month's invoice.
            # A shift of +1 moves the cost to the next month's invoice.
            for day in cross_over_day_specifiers:
                if day > 0:  # Day is from the start of the month
                    day_to_shift_map[month_key][day] = -1
                else:  # Day is from the end of the month
                    day_from_start = num_days_in_month + day + 1
                    day_to_shift_map[month_key][day_from_start] = 1

        return day_to_shift_map

    def _generate_hourly_data(self, **kwargs):
        """
        Generates hourly cost data, applying invoice date shifts for specific days.

        This generator function iterates through hourly usage data. For specific days
        defined in the 'cross_over' configuration, it can shift the cost to the
        invoice of the previous or next month. This is useful for simulating billing
        scenarios where costs incurred at the very beginning or end of a month are
        billed in an adjacent month.

        The behavior is controlled by `self._cross_over_metadata` (from YAML):
        - `month` (str): 'current', 'previous', or 'all'. Determines to which month(s)
                         the cross-over logic should apply. Defaults to 'all'.
        - `days` (list[int]): A list of day specifiers.
                            - Positive numbers (e.g., 2) shift costs to the *previous* month.
                            - Negative numbers (e.g., -1 for the last day) count from the end of the month and shift
                            costs to the *next* month.
        - `overwrite` (bool): If True, the original cost entry is replaced by the
                              shifted one. If False, the original is kept, and a new
                              shifted entry is also created.

        Note:
            This function assumes that all data in `self.hours` belongs to the
            same calendar month. Behavior is undefined if hours span a month boundary.
        """

        if not self.hours:
            return

        # --- 1. Initialization and Setup ---
        overwrite = self._cross_over_metadata.get("overwrite", False)
        cross_over_day_specifiers = self._cross_over_metadata.get("days", [])

        # --- 2. Calculate Invoice Shifts  ---
        start_dt = self.hours[0].get("start")
        end_dt = self.hours[-1].get("start")
        day_to_shift_map = self._get_day_to_shift_map(cross_over_day_specifiers, start_dt, end_dt)

        # --- 3. Process Each Hour, Applying Invoice Shifts Where Necessary ---
        for hour in self.hours:
            start, end = hour.get("start"), hour.get("end")
            row = self._init_data_row(start, end)
            row = self._update_data(row)

            # Check if the current day has a defined shift
            if shift_direction := day_to_shift_map.get(start.month, {}).get(start.day):
                # This is a cross-over day, so yield the modified row.
                yield apply_different_invoice_month(row, shift_direction)
                if overwrite:
                    # If overwriting, skip yielding the original row.
                    continue

            # Yield the original row (always, unless it was overwritten).
            yield row
