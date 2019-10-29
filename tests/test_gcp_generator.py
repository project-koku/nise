import json
from datetime import datetime, timedelta
from unittest import TestCase


from faker import Faker

# from nise.generators.generator import AbstractGenerator
from nise.generators.gcp import (CloudStorageGenerator,
                                 ComputeEngineGenerator,
                                 GCP_REPORT_COLUMNS,
                                 ProjectGenerator)

fake = Faker()


class TestGCPGenerator(TestCase):
    """Tests for the GCP Generator."""

    def setUp(self):
        """shared attributes."""
        self.account = '{}-{}'.format(fake.word(), fake.word())  # pylint: disable=maybe-no-member
        project_generator = ProjectGenerator(self.account)
        self.project = project_generator.generate_projects(num_projects=1)[0]
        self.attributes = {
            'Line Item': fake.word(),
            'Measurement1': fake.word(),
            'Measurement1 Total Consumption': fake.word(),
            'Measurement1 Units': fake.word(),
            'Cost': fake.word(),
            'Currency': fake.word(),
            'Credit1': fake.word(),
            'Credit1 Amount': fake.word(),
            'Credit1 Currency': fake.word(),
            'Description': fake.word()
        }
        self.now = datetime.now().replace(microsecond=0, second=0, minute=0)
        self.yesterday = self.now - timedelta(days=1)

    def test_cloud_storage_init_with_attributes(self):
        """Test the init with attribute for Cloud Storage."""

        generator = CloudStorageGenerator(self.yesterday, self.now,
                                          self.project, attributes=self.attributes)
        generated_data = generator.generate_data()
        self.assertEqual(generated_data[self.yesterday][0]['Line Item'],
                         self.attributes['Line Item'])
        self.assertEqual(generated_data[self.yesterday][0]['Measurement1'],
                         self.attributes['Measurement1'])
        self.assertEqual(generated_data[self.yesterday][0]['Currency'],
                         self.attributes['Currency'])

    def test_compute_engine_init_with_attributes(self):
        """Test the init with attribute for Compute Engine."""

        generator = ComputeEngineGenerator(self.yesterday, self.now,
                                           self.project, attributes=self.attributes)
        generated_data = generator.generate_data()
        self.assertEqual(generated_data[self.yesterday][0]['Line Item'],
                         self.attributes['Line Item'])
        self.assertEqual(generated_data[self.yesterday][0]['Measurement1'],
                         self.attributes['Measurement1'])
        self.assertEqual(generated_data[self.yesterday][0]['Currency'],
                         self.attributes['Currency'])

    def test_set_hours_invalid_start(self):
        """Test that the start date must be a date object."""
        with self.assertRaises(ValueError):
            generator = CloudStorageGenerator('invalid', self.now,
                                  self.project)
            generator.generate_data()

    def test_set_hours_invalid_end(self):
        """Test that the end date must be a date object."""
        with self.assertRaises(ValueError):
            generator = CloudStorageGenerator(self.now, 'invalid',
                                              self.project)
            generator.generate_data()


    def test_set_hours_none_start(self):
        """Test that the start date is not None."""
        with self.assertRaises(ValueError):
            generator = CloudStorageGenerator(None, self.now,
                                              self.project)
            generator.generate_data()


    def test_set_hours_none_end(self):
        """Test that the end date is not None."""
        with self.assertRaises(ValueError):
            generator = CloudStorageGenerator(self.now, None,
                                              self.project)
            generator.generate_data()
