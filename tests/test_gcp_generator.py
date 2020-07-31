import os
import tempfile
from datetime import datetime
from datetime import timedelta
from unittest import TestCase

from faker import Faker
from nise.generators.gcp import CloudStorageGenerator
from nise.generators.gcp import ComputeEngineGenerator
from nise.generators.gcp import ProjectGenerator

fake = Faker()


def create_test_config(**kwargs):
    """Create a test config. Users should remove the file at the end of the test."""
    test_yaml = """
---
generators:
  - {generator}:
      Line Item: {Line Item}
      Measurement1: {Measurement1}
      Measurement1 Total Consumption: {Measurement1 Total Consumption}
      Measurement1 Units: "{Measurement1 Units}"
      Cost: {Cost}
      Currency: {Currency}
      Description: {Description}
"""

    _, tmp_filename = tempfile.mkstemp()
    with open(tmp_filename, "w+") as tmp_handle:
        tmp_handle.write(test_yaml.format(**kwargs))

    return tmp_filename


class TestGCPGenerator(TestCase):
    """Tests for the GCP Generator."""

    def setUp(self):
        """shared attributes."""
        self.account = "{}-{}".format(fake.word(), fake.word())
        project_generator = ProjectGenerator(self.account)
        self.project = project_generator.generate_projects(num_projects=1)[0]
        self.test_config_kwargs = {
            "generator": "ComputeEngineGenerator",
            "Line Item": fake.word(),
            "Measurement1": fake.word(),
            "Measurement1 Total Consumption": fake.word(),
            "Measurement1 Units": fake.word(),
            "Cost": fake.pyint(),
            "Currency": fake.currency()[0],
            "Description": fake.sentence(),
        }
        self.now = datetime.now().replace(microsecond=0, second=0, minute=0)
        self.yesterday = self.now - timedelta(days=1)

    def test_cloud_storage_init_with_attributes(self):
        """Test the init with attribute for Cloud Storage."""

        test_args = self.test_config_kwargs
        test_args["generator"] = "CloudStorageGenerator"
        test_config = create_test_config(**test_args)
        generator = CloudStorageGenerator(self.yesterday, self.now, self.project, user_config=test_config)
        generated_data = generator.generate_data()
        self.assertEqual(generated_data[self.yesterday][0]["Line Item"], self.test_config_kwargs["Line Item"])
        self.assertEqual(generated_data[self.yesterday][0]["Measurement1"], self.test_config_kwargs["Measurement1"])
        self.assertEqual(generated_data[self.yesterday][0]["Currency"], self.test_config_kwargs["Currency"])
        os.remove(test_config)

    def test_compute_engine_init_with_attributes(self):
        """Test the init with attribute for Compute Engine."""

        test_config = create_test_config(**self.test_config_kwargs)
        generator = ComputeEngineGenerator(self.yesterday, self.now, self.project, user_config=test_config)
        generated_data = generator.generate_data()
        self.assertEqual(generated_data[self.yesterday][0]["Line Item"], self.test_config_kwargs["Line Item"])
        self.assertEqual(generated_data[self.yesterday][0]["Measurement1"], self.test_config_kwargs["Measurement1"])
        self.assertEqual(generated_data[self.yesterday][0]["Currency"], self.test_config_kwargs["Currency"])
        os.remove(test_config)

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
