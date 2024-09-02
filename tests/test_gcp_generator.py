import json
from datetime import datetime
from datetime import timedelta
from unittest import TestCase

from faker import Faker
from nise.generators.gcp import CloudStorageGenerator
from nise.generators.gcp import ComputeEngineGenerator
from nise.generators.gcp import GCPDatabaseGenerator
from nise.generators.gcp import GCPNetworkGenerator
from nise.generators.gcp import JSONLCloudStorageGenerator
from nise.generators.gcp import JSONLComputeEngineGenerator
from nise.generators.gcp import JSONLGCPDatabaseGenerator
from nise.generators.gcp import JSONLGCPNetworkGenerator
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
            "labels": [{"cody": "test"}],
            "instance-type": "test",
        }
        self.usage_attributes = {
            "currency": fake.currency_code(),
            "currency_conversion_rate": 1,
            "cost_type": "regular",
            "usage.amount": 10,
            "usage.amount_in_pricing_units": 10,
            "price": 2,
            "usage.pricing_unit": "hour",
        }
        self.sku_attributes = {
            "currency": fake.currency_code(),
            "currency_conversion_rate": 1,
            "cost_type": "regular",
            "usage.amount": 10,
            "usage.amount_in_pricing_units": 10,
            "price": 2,
            "sku_id": "CF4E-A0C7-E3BF",
        }
        self.resource_attributes = {
            "currency": fake.currency_code(),
            "currency_conversion_rate": 1,
            "cost_type": "regular",
            "usage.amount": 10,
            "usage.amount_in_pricing_units": 10,
            "price": 2,
            "sku_id": "CF4E-A0C7-E3BF",
            "resource.name": "resource-name",
            "resource.global_name": "global-name",
            "resource_level": True,
            "price.effective_price": 0.04524,
        }
        self.now = datetime.now().replace(microsecond=0, second=0, minute=0)
        self.yesterday = self.now - timedelta(days=1)
        self.currency = "USD"

    def test_cloud_storage_init_with_attributes(self):
        """Test the init with attribute for Cloud Storage."""

        generator = CloudStorageGenerator(
            self.yesterday, self.now, self.currency, self.project, attributes=self.attributes
        )
        generated_data = generator.generate_data()
        list_data = list(generated_data)
        self.assertEqual(list_data[0]["cost"], self.attributes["cost"])

    def test_cloud_storage_init_with_usage_attributes(self):
        """Test the init with usage attribute for Cloud Storage."""
        generator = CloudStorageGenerator(
            self.yesterday, self.now, self.currency, self.project, attributes=self.usage_attributes
        )
        generated_data = generator.generate_data()
        list_data = list(generated_data)
        self.assertEqual(list_data[0]["cost"], self.usage_attributes["usage.amount"] * self.usage_attributes["price"])

    def test_jsonl_cloud_storage_init_with_attributes(self):
        """Test the init with attribute for JSONL Cloud Storage."""
        generator = JSONLCloudStorageGenerator(
            self.yesterday, self.now, self.currency, self.project, attributes=self.attributes
        )
        generated_data = generator.generate_data()
        list_data = list(generated_data)
        self.assertEqual(list_data[0]["cost"], self.attributes["cost"])

    def test_jsonl_cloud_storage_init_with_usage_attributes(self):
        """Test the init with usage attribute for JSONL Cloud Storage."""
        generator = JSONLCloudStorageGenerator(
            self.yesterday, self.now, self.currency, self.project, attributes=self.usage_attributes
        )
        generated_data = generator.generate_data()
        list_data = list(generated_data)
        self.assertEqual(list_data[0]["cost"], self.usage_attributes["usage.amount"] * self.usage_attributes["price"])

    def test_compute_engine_init_with_attributes(self):
        """Test the init with attribute for Compute Engine."""

        generator = ComputeEngineGenerator(
            self.yesterday, self.now, self.currency, self.project, attributes=self.attributes
        )
        generated_data = generator.generate_data()
        list_data = list(generated_data)
        self.assertEqual(list_data[0]["cost"], self.attributes["cost"])

    def test_compute_engine_init_with_usage_attributes(self):
        """Test the init with usage attributes for Compute Engine."""
        generator = ComputeEngineGenerator(
            self.yesterday, self.now, self.currency, self.project, attributes=self.usage_attributes
        )
        generated_data = generator.generate_data()
        list_data = list(generated_data)
        self.assertEqual(list_data[0]["cost"], self.usage_attributes["usage.amount"] * self.usage_attributes["price"])
        self.assertIn("price.effective_price", list_data[0])

    def test_compute_engine_init_with_sku_attributes(self):
        """Test the init with sku attributes for Compute Engine."""
        generator = ComputeEngineGenerator(
            self.yesterday, self.now, self.currency, self.project, attributes=self.sku_attributes
        )
        generated_data = generator.generate_data()
        list_data = list(generated_data)
        self.assertEqual(list_data[0]["cost"], self.sku_attributes["usage.amount"] * self.sku_attributes["price"])

    def test_compute_engine_init_with_resource_attributes(self):
        """Test the init with resource attributes for Compute Engine."""
        generator = ComputeEngineGenerator(
            self.yesterday, self.now, self.currency, self.project, attributes=self.resource_attributes
        )
        generated_data = generator.generate_data()
        list_data = list(generated_data)
        self.assertEqual(
            list_data[0]["cost"], self.resource_attributes["usage.amount"] * self.resource_attributes["price"]
        )

    def test_jsonl_compute_engine_init_with_attributes(self):
        """Test the init with attribute for JSONL Compute Engine."""
        generator = JSONLComputeEngineGenerator(
            self.yesterday, self.now, self.currency, self.project, attributes=self.attributes
        )
        generated_data = generator.generate_data()
        list_data = list(generated_data)
        self.assertEqual(list_data[0]["cost"], self.attributes["cost"])

    def test_jsonl_compute_engine_init_with_usage_attributes(self):
        """Test the init with attribute for JSONL Compute Engine."""
        generator = JSONLComputeEngineGenerator(
            self.yesterday, self.now, self.currency, self.project, attributes=self.usage_attributes
        )
        generated_data = generator.generate_data()
        list_data = list(generated_data)
        self.assertEqual(list_data[0]["cost"], self.usage_attributes["usage.amount"] * self.usage_attributes["price"])

    def test_jsonl_compute_engine_init_with_sku_attributes(self):
        """Test the init with attribute for JSONL Compute Engine."""
        generator = JSONLComputeEngineGenerator(
            self.yesterday, self.now, self.currency, self.project, attributes=self.sku_attributes
        )
        generated_data = generator.generate_data()
        list_data = list(generated_data)
        self.assertEqual(list_data[0]["cost"], self.sku_attributes["usage.amount"] * self.sku_attributes["price"])

    def test_jsonl_compute_engine_init_with_resource_attributes(self):
        """Test the init with attribute for JSONL Compute Engine."""
        generator = JSONLComputeEngineGenerator(
            self.yesterday, self.now, self.currency, self.project, attributes=self.resource_attributes
        )
        generated_data = generator.generate_data()
        list_data = list(generated_data)
        self.assertEqual(
            list_data[0]["cost"], self.resource_attributes["usage.amount"] * self.resource_attributes["price"]
        )

    def test_network_generator_init_with_attributes(self):
        """Test the init with attribute for GCP Network Generator."""
        generator = GCPNetworkGenerator(
            self.yesterday, self.now, self.currency, self.project, attributes=self.attributes
        )
        generated_data = generator.generate_data()
        list_data = list(generated_data)
        self.assertEqual(list_data[0]["cost"], self.attributes["cost"])

    def test_network_generator_init_with_usage_attributes(self):
        """Test the init with usage attributes for GCP Network Generator."""
        generator = GCPNetworkGenerator(
            self.yesterday, self.now, self.currency, self.project, attributes=self.usage_attributes
        )
        generated_data = generator.generate_data()
        list_data = list(generated_data)
        self.assertEqual(list_data[0]["cost"], self.usage_attributes["usage.amount"] * self.usage_attributes["price"])

    def test_network_generator_init_with_resource_attributes(self):
        """Test the init with resource attributes for GCP Network Generator."""
        generator = GCPNetworkGenerator(
            self.yesterday, self.now, self.currency, self.project, attributes=self.resource_attributes
        )
        generated_data = generator.generate_data()
        list_data = list(generated_data)
        self.assertEqual(
            list_data[0]["cost"], self.resource_attributes["usage.amount"] * self.resource_attributes["price"]
        )

    def test_jsonl_network_generator_init_with_resource_attributes(self):
        """Test the init with resource attribute for JSONL GCP Network Generator."""
        generator = JSONLGCPNetworkGenerator(
            self.yesterday, self.now, self.currency, self.project, attributes=self.resource_attributes
        )
        generated_data = generator.generate_data()
        list_data = list(generated_data)
        self.assertEqual(
            list_data[0]["cost"], self.resource_attributes["usage.amount"] * self.resource_attributes["price"]
        )

    def test_jsonl_network_generator_init_with_attributes(self):
        """Test the init with attribute for JSONL GCP Network Generator."""
        generator = JSONLGCPNetworkGenerator(
            self.yesterday, self.now, self.currency, self.project, attributes=self.attributes
        )
        generated_data = generator.generate_data()
        list_data = list(generated_data)
        self.assertEqual(list_data[0]["cost"], self.attributes["cost"])

    def test_jsonl_network_generator_init_with_usage_attributes(self):
        """Test the init with attribute for JSONL GCP Network Generator."""
        generator = JSONLGCPNetworkGenerator(
            self.yesterday, self.now, self.currency, self.project, attributes=self.usage_attributes
        )
        generated_data = generator.generate_data()
        list_data = list(generated_data)
        self.assertEqual(list_data[0]["cost"], self.usage_attributes["usage.amount"] * self.usage_attributes["price"])

    def test_database_generator_init_with_attributes(self):
        """Test the init with attribute for GCP Database Generator."""
        generator = GCPDatabaseGenerator(
            self.yesterday, self.now, self.currency, self.project, attributes=self.attributes
        )
        generated_data = generator.generate_data()
        list_data = list(generated_data)
        self.assertEqual(list_data[0]["cost"], self.attributes["cost"])

    def test_database_generator_init_with_usage_attributes(self):
        """Test the init with usage attributes for GCP Database Generator."""
        generator = GCPDatabaseGenerator(
            self.yesterday, self.now, self.currency, self.project, attributes=self.usage_attributes
        )
        generated_data = generator.generate_data()
        list_data = list(generated_data)
        self.assertEqual(list_data[0]["cost"], self.usage_attributes["usage.amount"] * self.usage_attributes["price"])

    def test_database_generator_init_with_resource_attributes(self):
        """Test the init with resource attributes for GCP Database Generator."""
        generator = GCPDatabaseGenerator(
            self.yesterday, self.now, self.currency, self.project, attributes=self.resource_attributes
        )
        generated_data = generator.generate_data()
        list_data = list(generated_data)
        self.assertEqual(
            list_data[0]["cost"], self.resource_attributes["usage.amount"] * self.resource_attributes["price"]
        )

    def test_jsonl_database_generator_init_with_resource_attributes(self):
        """Test the init with resource attribute for JSONL GCP Database Generator."""
        generator = JSONLGCPDatabaseGenerator(
            self.yesterday, self.now, self.currency, self.project, attributes=self.resource_attributes
        )
        generated_data = generator.generate_data()
        list_data = list(generated_data)
        self.assertEqual(
            list_data[0]["cost"], self.resource_attributes["usage.amount"] * self.resource_attributes["price"]
        )

    def test_jsonl_database_generator_init_with_attributes(self):
        """Test the init with attribute for JSONL GCP Database Generator."""
        generator = JSONLGCPDatabaseGenerator(
            self.yesterday, self.now, self.currency, self.project, attributes=self.attributes
        )
        generated_data = generator.generate_data()
        list_data = list(generated_data)
        self.assertEqual(list_data[0]["cost"], self.attributes["cost"])

    def test_jsonl_database_generator_init_with_usage_attributes(self):
        """Test the init with attribute for JSONL GCP Database Generator."""
        generator = JSONLGCPDatabaseGenerator(
            self.yesterday, self.now, self.currency, self.project, attributes=self.usage_attributes
        )
        generated_data = generator.generate_data()
        list_data = list(generated_data)
        self.assertEqual(list_data[0]["cost"], self.usage_attributes["usage.amount"] * self.usage_attributes["price"])

    def test_set_hours_invalid_start(self):
        """Test that the start date must be a date object."""
        with self.assertRaises(ValueError):
            generator = CloudStorageGenerator("invalid", self.now, None, self.project)
            generator.generate_data()

    def test_set_hours_invalid_end(self):
        """Test that the end date must be a date object."""
        with self.assertRaises(ValueError):
            generator = CloudStorageGenerator(self.now, "invalid", None, self.project)
            generator.generate_data()

    def test_set_hours_none_start(self):
        """Test that the start date is not None."""
        with self.assertRaises(ValueError):
            generator = CloudStorageGenerator(None, self.now, self.currency, self.project)
            generator.generate_data()

    def test_set_hours_none_end(self):
        """Test that the end date is not None."""
        with self.assertRaises(ValueError):
            generator = CloudStorageGenerator(self.now, None, None, self.project)
            generator.generate_data()

    def test_gcp_generators_with_credit_attributes(self):
        """Test generators with credit attributes."""
        expected_credit_amount = -10
        attributes = {
            "currency": fake.currency_code(),
            "currency_conversion_rate": 1,
            "cost_type": "regular",
            "usage.amount": 10,
            "usage.amount_in_pricing_units": 10,
            "price": 2,
            "usage.pricing_unit": "hour",
            "credit_amount": expected_credit_amount,
        }
        generators_list = [CloudStorageGenerator, ComputeEngineGenerator, GCPDatabaseGenerator, GCPNetworkGenerator]
        for generator in generators_list:
            gen_handler = generator(self.yesterday, self.now, self.currency, self.project, attributes=attributes)
            generated_data = gen_handler.generate_data()
            list_data = list(generated_data)
            credit_rows = []
            for row in list_data:
                if row.get("credits") != "[]":
                    credit_dict = row.get("credits").replace("'", '"').strip("][")
                    credit_dict = json.loads(credit_dict)
                    credit_amount = credit_dict.get("amount", 0)
                    credit_rows.append(credit_amount)
            self.assertEqual(sum(credit_rows), expected_credit_amount)

    def test_gcp_jsonl_generators_with_credit_attributes(self):
        """Test json generators with credit attributes."""
        expected_credit_amount = -10
        attributes = {
            "currency": fake.currency_code(),
            "currency_conversion_rate": 1,
            "cost_type": "regular",
            "usage.amount": 10,
            "usage.amount_in_pricing_units": 10,
            "price": 2,
            "usage.pricing_unit": "hour",
            "credit_amount": expected_credit_amount,
        }
        generators_list = [JSONLCloudStorageGenerator, JSONLComputeEngineGenerator, JSONLGCPDatabaseGenerator]
        for generator in generators_list:
            gen_handler = generator(self.yesterday, self.now, self.currency, self.project, attributes=attributes)
            generated_data = gen_handler.generate_data()
            num_invoice_months = gen_handler._gcp_find_invoice_months_in_date_range()
            list_data = list(generated_data)
            credit_rows = []
            for row in list_data:
                credit_amount = row.get("credits", {}).get("amount", 0)
                credit_rows.append(credit_amount)
            self.assertEqual(sum(credit_rows), expected_credit_amount * len(num_invoice_months))
