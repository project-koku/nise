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
"""Module for generating GCP Projects."""
from random import choice

from faker import Faker


class ProjectGenerator:
    """Generator for GCP Compute Engine data."""

    fake_words = [Faker().word() for i in range(6)]
    PROJECT_INFO = (  # id -  name, labels, ancestry_numbers
        (
            f"{fake_words[0]}-{fake_words[1]}-{fake_words[2]}",
            f"{fake_words[0]}-{fake_words[1]}-{fake_words[2]}",
            "[]",
            "",
        ),
        (
            f"{fake_words[3]}-{fake_words[4]}-{fake_words[5]}",
            f"{fake_words[3]}-{fake_words[4]}-{fake_words[5]}",
            "[{'key': 'foo', 'value': 'bar'}]",
            "",
        ),
    )

    LOCATION = (("us-central1", "US", "us-central1", ""),)  # (Location, Country, Region, Zone)

    def __init__(self, account):
        """Initialize GCP Project Generator."""
        self.account = account
        self.fake = Faker()

    def generate_projects(self, num_projects=2):
        """Generate GCP project information."""
        projects = []
        for _ in range(num_projects):
            proj = choice(self.PROJECT_INFO)
            project_name = proj[1]
            project_id = proj[0]
            formatted_labels = proj[2]
            project_an = proj[3]
            location = choice(self.LOCATION)
            project = {
                "billing_account_id": self.account,
                "project.id": project_id,
                "project.name": project_name,
                "project.labels": formatted_labels,
                "project.ancestry_numbers": project_an,
                "location.location": location[0],
                "location.country": location[1],
                "location.region": location[2],
                "location.zone": location[3],
            }
            projects.append(project)

        return projects


class JSONLProjectGenerator:
    """Generator for GCP Compute Engine data."""

    fake_words = [Faker().word() for i in range(6)]
    PROJECT_INFO = (  # id -  name, labels, ancestry_numbers
        (
            f"{fake_words[0]}-{fake_words[1]}-{fake_words[2]}",
            f"{fake_words[0]}-{fake_words[1]}-{fake_words[2]}",
            [],
            "",
        ),
        (
            f"{fake_words[3]}-{fake_words[4]}-{fake_words[5]}",
            f"{fake_words[3]}-{fake_words[4]}-{fake_words[5]}",
            [{"key": "foo", "value": "bar"}],
            "",
        ),
    )

    LOCATION = (("us-central1", "US", "us-central1", ""),)  # (Location, Country, Region, Zone)

    def __init__(self, account):
        """Initialize GCP Project Generator."""
        self.account = account
        self.fake = Faker()

    def generate_projects(self, num_projects=2):
        """Generate GCP project information."""
        projects = []
        for _ in range(num_projects):
            proj = choice(self.PROJECT_INFO)
            project_name = proj[1]
            project_id = proj[0]
            formatted_labels = proj[2]
            project_an = proj[3]
            location_choice = choice(self.LOCATION)
            project = {}
            project["id"] = project_id
            project["name"] = project_name
            project["labels"] = formatted_labels
            project["ancestry_numbers"] = project_an
            location = {}
            location["location"] = location_choice[0]
            location["country"] = location_choice[1]
            location["region"] = location_choice[2]
            location["zone"] = location_choice[3]
            project_row = {"billing_account_id": self.account, "project": project, "location": location}
            projects.append(project_row)

        return projects
