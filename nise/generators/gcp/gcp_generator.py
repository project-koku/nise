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
"""Abstract class for gcp data generation."""
import datetime
from abc import abstractmethod

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

    TEMPLATE = "gcp.j2"

    # Not yet implemented.
    TEMPLATE_KWARGS = {}

    def __init__(self, start_date, end_date, project, user_config=None):
        """
        Initialize the generator.

        Args:
            start_date (datetime): Day to start generating reports from.
            end_date (datetime): Last day to generate reports for.
            project (int): GCP project number
        """
        self.TEMPLATE_KWARGS["project_gens"] = [{}]
        super().__init__(start_date, end_date, user_config=user_config)

        self.project = project

    def _format_config(self, config):
        """Handle special cases in the config layout."""
        return config

    def _create_days_list(self, start_date, end_date):
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
