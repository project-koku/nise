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
