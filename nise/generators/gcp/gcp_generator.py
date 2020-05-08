"""Abstract class for gcp data generation."""
import datetime
from abc import abstractmethod
from random import randint

from nise.generators.generator import AbstractGenerator


GCP_REPORT_COLUMNS = (
    "Account ID",
    "Line Item",
    "Start Time",
    "End Time",
    "Project",
    "Measurement1",
    "Measurement1 Total Consumption",
    "Measurement1 Units",
    "Credit1",
    "Credit1 Amount",
    "Credit1 Currency",
    "Cost",
    "Currency",
    "Project Number",
    "Project ID",
    "Project Name",
    "Project Labels",
    "Description",
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
        for column in GCP_REPORT_COLUMNS:
            row[column] = ""
            if column == "Start Time":
                row[column] = GCPGenerator.timestamp(start)
            elif column == "End Time":
                row[column] = GCPGenerator.timestamp(end)
        row.update(self.project)
        return row

    def _add_common_usage_info(self, row, start, end, **kwargs):
        """Not needed for GCP."""

    @abstractmethod
    def _update_data(self, row, start, end, **kwargs):
        """Update a data row."""

    def _generate_hourly_data(self, **kwargs):
        """Not needed for GCP."""
