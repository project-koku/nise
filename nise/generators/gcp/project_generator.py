"""Module for generating GCP Projects."""
from faker import Faker
from random import choice

class ProjectGenerator:
    """Generator for GCP Compute Engine data."""

    PROJECT_INFO = ( # id -  name, labels, ancestry_numbers
        ("doug-cost-test","Doug-cost-test", "[]", ""),
        ("doug-test-proj", "Doug-test-proj", "[{'key': 'foo', 'value': 'bar'}]", ""),
    )

    LOCATION = ( # (Location, Country, Region, Zone)
        ("us-central1", "US","us-central1",""),
    )

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
                "Billing Account ID": self.account,
                "Project ID": project_id,
                "Project Name": project_name,
                "Project Labels": formatted_labels,
                "Project Ancestry Numbers": project_an,
                "Location": location[0],
                "Country": location[1],
                "Region": location[2],
                "Zone": location[3],
            }
            projects.append(project)

        return projects
