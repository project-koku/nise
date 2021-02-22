from datetime import datetime
from datetime import timedelta
from unittest import TestCase

from faker import Faker
from nise.generators.gcp import CloudStorageGenerator
from nise.generators.gcp import ComputeEngineGenerator
from nise.generators.gcp import JSONLCloudStorageGenerator
from nise.generators.gcp import JSONLComputeEngineGenerator
from nise.generators.gcp import JSONLProjectGenerator
from nise.generators.gcp import ProjectGenerator


fake = Faker()


class TestGCPGenerator(TestCase):
    """Tests for the GCP Generator."""

    def setUp(self):
        """shared attributes."""
        self.account = "{}-{}".format(fake.word(), fake.word())
        project_generator = ProjectGenerator(self.account)
        self.project = project_generator.generate_projects(num_projects=2)[0]
        jsonl_project_generator = JSONLProjectGenerator(self.account)
        self.jsonl_project = jsonl_project_generator
        self.attributes = {
            "cost": fake.pyint(),
            "currency": fake.currency_code(),
            "currency_conversion_rate": 1,
            "cost_type": "regular",
        }
        self.now = datetime.now().replace(microsecond=0, second=0, minute=0)
        self.yesterday = self.now - timedelta(days=1)

    def test_cloud_storage_init_with_attributes(self):  # Cloud storage not currently implemented
        """Test the init with attribute for Cloud Storage."""

        generator = CloudStorageGenerator(self.yesterday, self.now, self.project, attributes=self.attributes)
        generated_data = generator.generate_data()
        list_data = list(generated_data)
        self.assertEqual(list_data[0]["cost"], self.attributes["cost"])
        self.assertEqual(list_data[0]["currency"], self.attributes["currency"])

    def test_jsonl_cloud_storage_init_with_attributes(self):  # Cloud storage not currently implemented
        """Test the init with attribute for JSONL Cloud Storage."""
        generator = JSONLCloudStorageGenerator(self.yesterday, self.now, self.project, attributes=self.attributes)
        generated_data = generator.generate_data()
        list_data = list(generated_data)
        self.assertEqual(list_data[0]["cost"], self.attributes["cost"])
        self.assertEqual(list_data[0]["currency"], self.attributes["currency"])

    def test_compute_engine_init_with_attributes(self):
        """Test the init with attribute for Compute Engine."""

        generator = ComputeEngineGenerator(self.yesterday, self.now, self.project, attributes=self.attributes)
        generated_data = generator.generate_data()
        list_data = list(generated_data)
        self.assertEqual(list_data[0]["cost"], self.attributes["cost"])
        self.assertEqual(list_data[0]["currency"], self.attributes["currency"])

    def test_jsonl_compute_engine_init_with_attributes(self):
        """Test the init with attribute for JSONL Compute Engine."""
        generator = JSONLComputeEngineGenerator(self.yesterday, self.now, self.project, attributes=self.attributes)
        generated_data = generator.generate_data()
        list_data = list(generated_data)
        self.assertEqual(list_data[0]["cost"], self.attributes["cost"])
        self.assertEqual(list_data[0]["currency"], self.attributes["currency"])

    def test_set_hours_invalid_start(self):
        """Test that the start date must be a date object."""
        with self.assertRaises(ValueError):
            generator = CloudStorageGenerator("invalid", self.now, self.project)
            generator.generate_data()

    def test_set_hours_invalid_end(self):
        """Test that the end date must be a date object."""
        with self.assertRaises(ValueError):
            generator = CloudStorageGenerator(self.now, "invalid", self.project)
            generator.generate_data()

    def test_set_hours_none_start(self):
        """Test that the start date is not None."""
        with self.assertRaises(ValueError):
            generator = CloudStorageGenerator(None, self.now, self.project)
            generator.generate_data()

    def test_set_hours_none_end(self):
        """Test that the end date is not None."""
        with self.assertRaises(ValueError):
            generator = CloudStorageGenerator(self.now, None, self.project)
            generator.generate_data()
