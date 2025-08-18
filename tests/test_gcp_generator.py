import json
from datetime import datetime
from datetime import timedelta
from unittest import TestCase

from faker import Faker
from nise.generators.gcp.gcp_generator import apply_previous_invoice_month
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
        self.account = f"{fake.word()}-{fake.word()}"
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
            "cross_over_data": True,
            "service.description": "Fire",
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
            for row in list_data:
                credit_dict = row.get("credits").replace("'", '"').strip("][")
                credit_dict = json.loads(credit_dict)
                credit_amount = credit_dict.get("amount", 0)
                self.assertEqual(credit_amount, expected_credit_amount)

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
            list_data = list(generated_data)
            for row in list_data:
                credit_amount = row.get("credits", {}).get("amount", 0)
                self.assertEqual(credit_amount, expected_credit_amount)

    def test_apply_previous_invoice_month(self):
        invoice_month = "202508"
        expected_month = "202507"
        output = apply_previous_invoice_month({"invoice.month": invoice_month})
        self.assertEqual(expected_month, output.get("invoice.month"))
        output = apply_previous_invoice_month({"invoice": {"month": invoice_month}})
        self.assertEqual(expected_month, output.get("invoice", {}).get("month"))

    def test_apply_previous_invoice_month_no_invoice(self):
        input = {}
        output = apply_previous_invoice_month(input)
        self.assertEqual(input, output)

    def test_generate_hourly_data(self):
        """Test the _generate_hourly_data method."""
        generator = ComputeEngineGenerator(self.yesterday, self.now, self.currency, self.project, attributes={})

        hourly_data = list(generator._generate_hourly_data())

        expected_rows = len(generator.hours)
        self.assertEqual(len(hourly_data), expected_rows)

        for row in hourly_data:
            self.assertIn("usage_start_time", row)
            self.assertIn("usage_end_time", row)
            self.assertIn("export_time", row)
            self.assertIn("partition_date", row)
            self.assertIn("service.description", row)
            self.assertIn("sku.id", row)
            self.assertTrue(row["service.description"])  # Should not be empty
            self.assertTrue(row["sku.id"])  # Should not be empty

    def test_generate_hourly_data_with_cross_over(self):
        """Test the _generate_hourly_data method with cross_over_data enabled."""

        start_date = (self.now.replace(day=1) - timedelta(days=1)).replace(day=1)  # first of the previous month
        end_date = self.now
        previous_invoice_month = start_date.strftime("%Y%m")

        # only current month 1st and 2nd should have shifted invoice month
        expected_cross_over_days = [str(self.now.replace(day=1).date())]
        if self.now.day > 1:
            expected_cross_over_days.append(str(self.now.replace(day=2).date()))

        attributes = {"cross_over_data": True}
        generator = ComputeEngineGenerator(start_date, end_date, self.currency, self.project, attributes=attributes)
        hourly_data = list(generator._generate_hourly_data())

        expected_total_rows = len(generator.hours)
        expected_cross_over_rows = len(
            [
                h
                for h in generator.hours
                if h["start"].day in [1, 2] and h["start"].month == end_date.month and h["start"].year == end_date.year
            ]
        )
        expected_regular_rows = expected_total_rows - expected_cross_over_rows
        self.assertEqual(len(hourly_data), expected_total_rows)

        cross_over_rows = []
        regular_rows = []

        for row in hourly_data:
            if "invoice.month" in row:
                if row["usage_start_time"][:10] in expected_cross_over_days:
                    cross_over_rows.append(row)
                    continue
                regular_rows.append(row)

        self.assertEqual(len(cross_over_rows), expected_cross_over_rows)
        self.assertEqual(len(regular_rows), expected_regular_rows)
        for cross_row in cross_over_rows:
            self.assertEqual(cross_row["invoice.month"], previous_invoice_month)
        for regular_row in regular_rows:
            self.assertEqual(regular_row["invoice.month"], regular_row["usage_start_time"][:7].replace("-", ""))

    def test_generate_hourly_data_no_cross_over_not_current_month(self):
        """Test that cross_over_data are not generated when not current month."""
        start_date = datetime(2024, 1, 1, 0, 0, 0)
        end_date = datetime(2024, 1, 2, 23, 0, 0)

        attributes = {"cross_over": {"overwrite": True}}
        generator = ComputeEngineGenerator(start_date, end_date, self.currency, self.project, attributes=attributes)

        hourly_data = list(generator._generate_hourly_data())

        expected_rows = len(generator.hours)
        self.assertEqual(len(hourly_data), expected_rows)

        for row in hourly_data:
            self.assertEqual(row["invoice.month"], "202401")

    def test_generate_hourly_data_no_cross_over_not_first_two_days(self):
        """Test that cross_over_data are not generated when not on first or second day."""
        start_date = self.now.replace(day=3)
        end_date = self.now.replace(day=4)

        attributes = {"cross_over": {"overwrite": True}}
        generator = ComputeEngineGenerator(start_date, end_date, self.currency, self.project, attributes=attributes)

        hourly_data = list(generator._generate_hourly_data())

        expected_rows = len(generator.hours)
        self.assertEqual(len(hourly_data), expected_rows)

        for row in hourly_data:
            self.assertEqual(row["invoice.month"], start_date.strftime("%Y%m"))
