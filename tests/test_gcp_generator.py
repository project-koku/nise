import json
from datetime import datetime
from datetime import timedelta
from unittest import TestCase

from faker import Faker
from nise.generators.gcp.gcp_generator import apply_different_invoice_month
from nise.generators.gcp import CloudStorageGenerator
from nise.generators.gcp import ComputeEngineGenerator
from nise.generators.gcp import PersistentDiskGenerator
from nise.generators.gcp import GCPDatabaseGenerator
from nise.generators.gcp import GCPNetworkGenerator
from nise.generators.gcp import JSONLCloudStorageGenerator
from nise.generators.gcp import JSONLComputeEngineGenerator
from nise.generators.gcp import JSONLGCPDatabaseGenerator
from nise.generators.gcp import JSONLPersistentDiskGenerator
from nise.generators.gcp import JSONLGCPNetworkGenerator
from nise.generators.gcp import JSONLProjectGenerator
from nise.generators.gcp import ProjectGenerator

import itertools

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
        # Disk-specific attributes (usage.amount not allowed)
        self.disk_usage_attributes = {
            "currency": fake.currency_code(),
            "currency_conversion_rate": 1,
            "cost_type": "regular",
            "capacity": 50,
            "price": 2,
            "usage.pricing_unit": "gibibyte month",
        }
        self.disk_sku_attributes = {
            "currency": fake.currency_code(),
            "currency_conversion_rate": 1,
            "cost_type": "regular",
            "capacity": 75,
            "price": 2,
            "sku_id": "3C62-891B-C73C",
        }
        self.disk_resource_attributes = {
            "currency": fake.currency_code(),
            "currency_conversion_rate": 1,
            "cost_type": "regular",
            "capacity": 100,
            "price": 2,
            "sku_id": "D973-5D65-BAB2",
            "resource.name": "disk-resource-name",
            "resource.global_name": "/compute.googleapis.com/projects/test/zones/us-central1/disk/test-disk",
            "disk_id": "test-disk-123",
        }
        self.persistent_disk_attributes = {
            "disk_id": "test12345",
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

    def test_persistent_disk_init_with_attributes(self):
        """Test the init with attribute for Persistent Disk."""
        generator = PersistentDiskGenerator(
            self.yesterday, self.now, self.currency, self.project, attributes=self.attributes
        )
        generated_data = generator.generate_data()
        list_data = list(generated_data)
        self.assertEqual(list_data[0]["cost"], self.attributes["cost"])

    def test_persistent_disk_init_with_usage_attributes(self):
        """Test the init with usage attributes for Persistent Disk."""
        generator = PersistentDiskGenerator(
            self.yesterday, self.now, self.currency, self.project, attributes=self.disk_usage_attributes
        )
        generated_data = generator.generate_data()
        list_data = list(generated_data)
        expected_cost = list_data[0]["usage.amount_in_pricing_units"] * self.disk_usage_attributes["price"]
        self.assertEqual(list_data[0]["cost"], expected_cost)

    def test_persistent_disk_init_with_sku_attributes(self):
        """Test the init with sku attributes for Persistent Disk."""
        generator = PersistentDiskGenerator(
            self.yesterday, self.now, self.currency, self.project, attributes=self.disk_sku_attributes
        )
        generated_data = generator.generate_data()
        list_data = list(generated_data)
        expected_cost = list_data[0]["usage.amount_in_pricing_units"] * self.disk_sku_attributes["price"]
        self.assertEqual(list_data[0]["cost"], expected_cost)

    def test_persistent_disk_init_with_resource_attributes(self):
        """Test the init with resource attributes for Persistent Disk."""
        generator = PersistentDiskGenerator(
            self.yesterday, self.now, self.currency, self.project, attributes=self.disk_resource_attributes
        )
        generated_data = generator.generate_data()
        list_data = list(generated_data)
        expected_cost = list_data[0]["usage.amount_in_pricing_units"] * self.disk_resource_attributes["price"]
        self.assertEqual(list_data[0]["cost"], expected_cost)

    def test_jsonl_persistent_disk_init_with_attributes(self):
        """Test the init with attribute for JSONL Persistent Disk."""
        generator = JSONLPersistentDiskGenerator(
            self.yesterday, self.now, self.currency, self.project, attributes=self.attributes
        )
        generated_data = generator.generate_data()
        list_data = list(generated_data)
        self.assertEqual(list_data[0]["cost"], self.attributes["cost"])

    def test_jsonl_persistent_disk_init_with_usage_attributes(self):
        """Test the init with usage attributes for JSONL Persistent Disk."""
        generator = JSONLPersistentDiskGenerator(
            self.yesterday, self.now, self.currency, self.project, attributes=self.disk_usage_attributes
        )
        generated_data = generator.generate_data()
        list_data = list(generated_data)
        expected_cost = list_data[0]["usage"]["amount_in_pricing_units"] * self.disk_usage_attributes["price"]
        self.assertEqual(list_data[0]["cost"], expected_cost)

    def test_jsonl_persistent_disk_init_with_sku_attributes(self):
        """Test the init with sku attributes for JSONL Persistent Disk."""
        generator = JSONLPersistentDiskGenerator(
            self.yesterday, self.now, self.currency, self.project, attributes=self.disk_sku_attributes
        )
        generated_data = generator.generate_data()
        list_data = list(generated_data)
        expected_cost = list_data[0]["usage"]["amount_in_pricing_units"] * self.disk_sku_attributes["price"]
        self.assertEqual(list_data[0]["cost"], expected_cost)

    def test_jsonl_persistent_disk_init_with_resource_attributes(self):
        """Test the init with resource attributes for JSONL Persistent Disk."""
        generator = JSONLPersistentDiskGenerator(
            self.yesterday, self.now, self.currency, self.project, attributes=self.disk_resource_attributes
        )
        generated_data = generator.generate_data()
        list_data = list(generated_data)
        expected_cost = list_data[0]["usage"]["amount_in_pricing_units"] * self.disk_resource_attributes["price"]
        self.assertEqual(list_data[0]["cost"], expected_cost)

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

    def test_apply_different_invoice_month(self):
        """Test shifting the invoice month forward and backward."""
        invoice_month = "202508"

        test_cases = [
            # (invoice_shift, expected_month)
            (-1, "202507"),  # Shift backward
            (1, "202509"),  # Shift forward
        ]

        for shift, expected_month in test_cases:
            with self.subTest(shift=shift, expected=expected_month):
                # Test with flat structure: {"invoice.month": "..."}
                row_flat = {"invoice.month": invoice_month}
                output_flat = apply_different_invoice_month(row_flat, shift)
                self.assertEqual(expected_month, output_flat.get("invoice.month"))

                # Test with nested structure: {"invoice": {"month": "..."}}
                row_nested = {"invoice": {"month": invoice_month}}
                output_nested = apply_different_invoice_month(row_nested, shift)
                self.assertEqual(expected_month, output_nested.get("invoice", {}).get("month"))

    def test_apply_different_invoice_month_no_invoice(self):
        """Test that the function returns the original row when no invoice key is present."""
        input_row = {}
        shifts_to_test = [1, -1]

        for shift in shifts_to_test:
            with self.subTest(shift=shift):
                output = apply_different_invoice_month(input_row, shift)
                self.assertEqual(input_row, output)

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

    def test_generate_hourly_data_with_cross_over_all_months(self):
        """
        Verify cross-over for all months in both overwrite and duplicate modes.

        Ensures that for specified days, 'invoice.month' is correctly shifted
        to the previous month, respecting the 'overwrite' flag.
        """
        for overwrite_value in [True, False]:
            with self.subTest(overwrite=overwrite_value):
                start_date = datetime(2024, 1, 1, 0, 0, 0)
                end_date = datetime(2024, 1, 15, 2, 0, 0)
                cross_over_day_settings = [1, 3]
                expected_cross_over_days_str = [f"2024-01-{day:02d}" for day in cross_over_day_settings]
                shifted_invoice_month = "202312"
                original_invoice_month = "202401"

                attributes = {"cross_over": {"days": cross_over_day_settings, "overwrite": overwrite_value}}
                generator = ComputeEngineGenerator(
                    start_date, end_date, self.currency, self.project, attributes=attributes
                )
                hourly_data = list(generator._generate_hourly_data())

                # Calculate expected row counts
                expected_cross_over_hours = len(
                    [h for h in generator.hours if h["start"].day in cross_over_day_settings]
                )
                expected_regular_hours = len(generator.hours)

                if overwrite_value:
                    expected_total_rows = expected_regular_hours
                else:  # duplicate mode
                    expected_total_rows = expected_regular_hours + expected_cross_over_hours

                self.assertEqual(len(hourly_data), expected_total_rows)

                # Separate and verify the rows
                cross_over_rows = []
                regular_rows = []
                for row in hourly_data:
                    usage_day_str = row["usage_start_time"][:10]
                    invoice_month = row["invoice.month"]

                    if usage_day_str in expected_cross_over_days_str and invoice_month == shifted_invoice_month:
                        cross_over_rows.append(row)
                    else:
                        regular_rows.append(row)

                self.assertEqual(len(cross_over_rows), expected_cross_over_hours)

                if overwrite_value:
                    self.assertEqual(len(regular_rows), expected_regular_hours - expected_cross_over_hours)
                else:  # duplicate mode
                    self.assertEqual(len(regular_rows), expected_regular_hours)

                for cross_row in cross_over_rows:
                    self.assertEqual(cross_row["invoice.month"], shifted_invoice_month)
                for regular_row in regular_rows:
                    self.assertEqual(regular_row["invoice.month"], original_invoice_month)

    def test_generate_hourly_data_with_cross_over_current_month(self):
        """
        Verify cross-over for 'current' month in both overwrite and duplicate modes.

        Ensures that for specified days of the 'current' month, the invoice month
        is correctly shifted to the previous month, respecting the 'overwrite' flag.
        """
        for overwrite_value in [True, False]:
            with self.subTest(overwrite=overwrite_value):
                start_date = (self.now.replace(day=1) - timedelta(days=1)).replace(day=1)
                end_date = self.now
                previous_invoice_month = start_date.strftime("%Y%m")

                cross_over_day_settings = [1, 2, 5]
                expected_cross_over_days = [str(self.now.replace(day=day).date()) for day in cross_over_day_settings]

                attributes = {
                    "cross_over": {"month": "current", "days": cross_over_day_settings, "overwrite": overwrite_value}
                }
                generator = ComputeEngineGenerator(
                    start_date, end_date, self.currency, self.project, attributes=attributes
                )
                hourly_data = list(generator._generate_hourly_data())

                # Calculate expected row counts
                expected_cross_over_hours = len(
                    [h for h in generator.hours if h["start"].strftime("%Y-%m-%d") in expected_cross_over_days]
                )
                expected_regular_hours = len(generator.hours)
                if overwrite_value:
                    expected_total_rows = expected_regular_hours
                else:
                    expected_total_rows = expected_regular_hours + expected_cross_over_hours
                self.assertEqual(len(hourly_data), expected_total_rows)

                # Separate and verify the rows
                cross_over_rows = []
                regular_rows = []
                for row in hourly_data:
                    usage_day_str = row["usage_start_time"][:10]
                    invoice_month = row["invoice.month"]

                    if usage_day_str in expected_cross_over_days and invoice_month == previous_invoice_month:
                        cross_over_rows.append(row)
                    else:
                        regular_rows.append(row)

                self.assertEqual(len(cross_over_rows), expected_cross_over_hours)
                if overwrite_value:
                    self.assertEqual(len(regular_rows), expected_regular_hours - expected_cross_over_hours)
                else:
                    self.assertEqual(len(regular_rows), expected_regular_hours)

                for regular_row in regular_rows:
                    original_month = regular_row["usage_start_time"][:7].replace("-", "")
                    self.assertEqual(regular_row["invoice.month"], original_month)

    def test_generate_hourly_data_with_cross_over_all_months_to_next_month(self):
        """
        Verify cross-over feature shifting costs to the *next* month using negative day specifiers.

        Tests both overwrite=True and overwrite=False modes by shifting costs incurred at the end
        of a month to the following month's invoice.
        """
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 31, 23, 0, 0)
        # Shift the last day (-1) and third to last day (-3) of January (days 31 and 29).
        cross_over_day_settings = [-1, -3]
        expected_cross_over_days_of_month = [29, 31]
        expected_cross_over_days_str = [f"2024-01-{day}" for day in expected_cross_over_days_of_month]
        next_invoice_month = "202402"
        original_invoice_month = "202401"

        for overwrite_value in [True, False]:
            with self.subTest(overwrite=overwrite_value):
                attributes = {
                    "cross_over": {"month": "all", "days": cross_over_day_settings, "overwrite": overwrite_value}
                }

                generator = ComputeEngineGenerator(
                    start_date, end_date, self.currency, self.project, attributes=attributes
                )
                hourly_data = list(generator._generate_hourly_data())

                # Calculate expected row counts
                expected_cross_over_hours = len(
                    [h for h in generator.hours if h["start"].day in expected_cross_over_days_of_month]
                )
                expected_regular_hours = len(generator.hours)

                if overwrite_value:
                    expected_total_rows = expected_regular_hours
                else:
                    expected_total_rows = expected_regular_hours + expected_cross_over_hours

                self.assertEqual(len(hourly_data), expected_total_rows)

                # Separate and verify the rows
                cross_over_rows = []
                regular_rows = []
                for row in hourly_data:
                    usage_day_str = row["usage_start_time"][:10]
                    invoice_month = row["invoice.month"]

                    # A row is a "cross_over_row" if its day is a crossover day AND its invoice is shifted
                    if usage_day_str in expected_cross_over_days_str and invoice_month == next_invoice_month:
                        cross_over_rows.append(row)
                    else:
                        regular_rows.append(row)

                self.assertEqual(len(cross_over_rows), expected_cross_over_hours)
                # Verify the count of non-shifted rows
                if overwrite_value:
                    self.assertEqual(len(regular_rows), expected_regular_hours - expected_cross_over_hours)
                else:
                    self.assertEqual(len(regular_rows), expected_regular_hours)

                # Verify invoice months in the separated lists
                for cross_row in cross_over_rows:
                    self.assertEqual(cross_row["invoice.month"], next_invoice_month)
                for regular_row in regular_rows:
                    self.assertEqual(regular_row["invoice.month"], original_invoice_month)

    def test_generate_hourly_data_no_cross_over_not_specified_month(self):
        """
        Verify no cross-over occurs when the data's month doesn't match the setting.

        Tests that when `month` is set to "current" or "previous", no invoice shifts
        happen for data generated for other months (e.g., a month in the past).
        This is tested for both overwrite=True and overwrite=False.
        """
        month_params = ["current", "previous"]
        overwrite_params = [True, False]
        param_combinations = itertools.product(month_params, overwrite_params)

        # Use a fixed date range in the past that is neither 'current' nor 'previous'
        start_date = datetime(2024, 1, 1, 0, 0, 0)
        end_date = datetime(2024, 1, 2, 23, 0, 0)
        expected_invoice_month = "202401"

        for month_value, overwrite_value in param_combinations:
            with self.subTest(month=month_value, overwrite=overwrite_value):
                attributes = {"cross_over": {"month": month_value, "days": [1, 2, -3], "overwrite": overwrite_value}}

                generator = ComputeEngineGenerator(
                    start_date, end_date, self.currency, self.project, attributes=attributes
                )
                hourly_data = list(generator._generate_hourly_data())

                # The number of rows should be unchanged because the month doesn't match
                expected_rows = len(generator.hours)
                self.assertEqual(len(hourly_data), expected_rows)

                # All rows should have their original invoice month
                for row in hourly_data:
                    self.assertEqual(row["invoice.month"], expected_invoice_month)

    def test_generate_hourly_data_no_cross_over_not_specified_days(self):
        """
        Test that cross_over_data are not generated when not on specified day,
        for multiple `month` and `overwrite` param combinations.
        """
        month_params = ["current", "previous", None]
        overwrite_params = [True, False]

        param_combinations = itertools.product(month_params, overwrite_params)

        start_date = self.now.replace(day=3)
        end_date = self.now.replace(day=4)

        for month_value, overwrite_value in param_combinations:
            with self.subTest(month=month_value, overwrite=overwrite_value):
                attributes = {"cross_over": {"month": month_value, "days": [1, 2, 5], "overwrite": overwrite_value}}
                generator = ComputeEngineGenerator(
                    start_date, end_date, self.currency, self.project, attributes=attributes
                )

                hourly_data = list(generator._generate_hourly_data())

                expected_rows = len(generator.hours)
                self.assertEqual(len(hourly_data), expected_rows)

                for row in hourly_data:
                    self.assertEqual(row["invoice.month"], start_date.strftime("%Y%m"))

    def test_persistent_disk_validate_attributes_unsupported(self):
        """Test that unsupported attributes raise ValueError for Persistent Disk."""
        unsupported_attributes = {"usage.amount": 10, "usage.amount_in_pricing_units": 5, "capacity": 100}
        with self.assertRaises(ValueError) as context:
            PersistentDiskGenerator(
                self.yesterday, self.now, self.currency, self.project, attributes=unsupported_attributes
            )
        self.assertIn("usage.amount", str(context.exception))

    def test_persistent_disk_default_properties(self):
        """Test default properties for Persistent Disk."""
        generator = PersistentDiskGenerator(self.yesterday, self.now, self.currency, self.project, attributes={})
        self.assertIn("pvc-", generator.disk_id)
        self.assertIn(generator.capacity, generator.DEFAULT_CAPACITIES)
        self.assertIn(generator.region, generator.DEFAULT_REGIONS)
        self.assertIn(generator.sku_id, generator.SKU_DESCRIPTION.keys())
        self.assertIsNotNone(generator.usage_amount)
        self.assertIsNotNone(generator.usage_in_pricing_units)
        self.assertIsNotNone(generator.cost)

    def test_persistent_disk_custom_properties(self):
        """Test custom properties for Persistent Disk."""
        custom_attributes = {
            "disk_id": "custom-disk-123",
            "capacity": 500,
            "location.region": "us-east1",
            "sku_id": "3C62-891B-C73C",
        }
        generator = PersistentDiskGenerator(
            self.yesterday, self.now, self.currency, self.project, attributes=custom_attributes
        )

        self.assertEqual(generator.disk_id, "custom-disk-123")
        self.assertEqual(generator.capacity, 500)
        self.assertEqual(generator.region, "us-east1")
        self.assertEqual(generator.sku_id, "3C62-891B-C73C")

    def test_persistent_disk_usage_calculations(self):
        """Test usage amount and pricing calculations for Persistent Disk."""
        custom_attributes = {
            "capacity": 100,
        }
        generator = PersistentDiskGenerator(
            self.yesterday, self.now, self.currency, self.project, attributes=custom_attributes
        )
        expected_bytes = 100 * (1024**3)
        expected_usage = expected_bytes * 3600
        self.assertEqual(generator.usage_amount, expected_usage)
        self.assertIsInstance(generator.usage_in_pricing_units, float)
        self.assertGreater(generator.usage_in_pricing_units, 0)

    def test_persistent_disk_sku_descriptions(self):
        """Test SKU descriptions mapping for Persistent Disk."""
        generator = PersistentDiskGenerator(self.yesterday, self.now, self.currency, self.project, attributes={})
        for sku_id, description in generator.SKU_DESCRIPTION.items():
            generator.attributes = {"sku_id": sku_id}
            if hasattr(generator, "_sku_id"):
                delattr(generator, "_sku_id")
            if hasattr(generator, "_sku_description"):
                delattr(generator, "_sku_description")
            test_generator = PersistentDiskGenerator(
                self.yesterday, self.now, self.currency, self.project, attributes={"sku_id": sku_id}
            )
            self.assertEqual(test_generator.sku_description, description)

    def test_persistent_disk_resource_names(self):
        """Test resource name generation for Persistent Disk."""
        generator = PersistentDiskGenerator(self.yesterday, self.now, self.currency, self.project, attributes={})
        expected_pattern = (
            f"/compute.googleapis.com/projects/{generator.project_id}/zones/{generator.region}/disk/{generator.disk_id}"
        )
        self.assertEqual(generator._resource_global_name, expected_pattern)
        custom_attrs = {"resource.name": "my-custom-disk", "resource.global_name": "/custom/global/name"}
        custom_generator = PersistentDiskGenerator(
            self.yesterday, self.now, self.currency, self.project, attributes=custom_attrs
        )
        self.assertEqual(custom_generator._resource_name, "my-custom-disk")
        self.assertEqual(custom_generator._resource_global_name, "/custom/global/name")

    def test_persistent_disk_data_structure(self):
        """Test the data structure returned by Persistent Disk generator."""
        generator = PersistentDiskGenerator(self.yesterday, self.now, self.currency, self.project, attributes={})
        generated_data = generator.generate_data()
        list_data = list(generated_data)

        self.assertGreater(len(list_data), 0)
        first_row = list_data[0]
        self.assertEqual(first_row["service.description"], "Compute Engine")
        self.assertEqual(first_row["service.id"], "6F81-5844-456A")
        self.assertEqual(first_row["usage.unit"], "byte-seconds")
        self.assertEqual(first_row["usage.pricing_unit"], "gibibyte month")
        self.assertIsInstance(first_row["usage.amount"], (int, float))
        self.assertIsInstance(first_row["usage.amount_in_pricing_units"], float)
        self.assertIsInstance(first_row["cost"], float)
        self.assertEqual(first_row["cost_type"], "regular")
        self.assertEqual(first_row["currency_conversion_rate"], 1)
        self.assertIsNotNone(first_row["resource.name"])
        self.assertIsNotNone(first_row["resource.global_name"])

    def test_jsonl_persistent_disk_data_structure(self):
        """Test the data structure returned by JSONL Persistent Disk generator."""
        generator = JSONLPersistentDiskGenerator(self.yesterday, self.now, self.currency, self.project, attributes={})
        generated_data = generator.generate_data()
        list_data = list(generated_data)

        self.assertGreater(len(list_data), 0)
        first_row = list_data[0]
        self.assertIsInstance(first_row["service"], dict)
        self.assertEqual(first_row["service"]["description"], "Compute Engine")
        self.assertEqual(first_row["service"]["id"], "6F81-5844-456A")
        self.assertIsInstance(first_row["sku"], dict)
        self.assertIn("id", first_row["sku"])
        self.assertIn("description", first_row["sku"])
        self.assertIsInstance(first_row["usage"], dict)
        self.assertEqual(first_row["usage"]["unit"], "byte-seconds")
        self.assertEqual(first_row["usage"]["pricing_unit"], "gibibyte month")
        self.assertIn("amount", first_row["usage"])
        self.assertIn("amount_in_pricing_units", first_row["usage"])
        self.assertIsInstance(first_row["resource"], dict)
        self.assertIn("name", first_row["resource"])
        self.assertIn("global_name", first_row["resource"])
        self.assertIsInstance(first_row["invoice"], dict)
        self.assertIn("month", first_row["invoice"])
