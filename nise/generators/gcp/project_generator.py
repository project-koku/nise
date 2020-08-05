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
"""Module for generating GCP Projects."""
from faker import Faker


class ProjectGenerator:
    """Generator for GCP Compute Engine data."""

    def __init__(self, account):
        """Initialize GCP Project Generator."""
        self.account = account
        self.fake = Faker()

    def generate_projects(self, num_projects=1):
        """Generate GCP project information."""
        projects = []
        for _ in range(num_projects):
            project_number = self.fake.ean13()
            project_id = "{}-{}-{}".format(self.fake.word(), self.fake.word(), self.fake.ean8())
            labels = {self.fake.word(): self.fake.word(), self.fake.word(): self.fake.word()}
            formatted_labels = ";".join(f"{k}:{v}" for k, v in labels.items())
            project = {
                "Account ID": self.account,
                "Project": project_number,
                "Project Number": project_number,
                "Project ID": project_id,
                "Project Name": project_id,
                "Project Labels": formatted_labels,
            }
            projects.append(project)

        return projects
