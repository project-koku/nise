"""Abstract class for gcp data generation."""
import datetime
from abc import abstractmethod
from random import randint

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


class GCPGenerator(AbstractGenerator):
    """Abstract class for GCP generators."""

    def __init__(self, start_date, end_date, project, attributes=None):
        """
        Initialize the generator.

        Args:
            start_date (datetime): Day to start generating reports from.
            end_date (datetime): Last day to generate reports for.
            account (string): Name of the account
            project_number (int): GCP project number
            project_id (string): GCP project id
            num_instances (int): number of instances to generate fake data for.

        """
        super().__init__(start_date, end_date)
        self.project = project
        self.num_instances = 1 if attributes else randint(2, 60)
        self.attributes = attributes
        self.column_labels = GCP_REPORT_COLUMNS

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
        time_bill_start = start + datetime.timedelta(hours=randint(1, 23))
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

    def _add_common_usage_info(self, row, start, end, **kwargs):
        """Not needed for GCP."""

    @abstractmethod
    def _update_data(self, row, start, end, **kwargs):
        """Update a data row."""

    def _generate_hourly_data(self, **kwargs):
        """Not needed for GCP."""
