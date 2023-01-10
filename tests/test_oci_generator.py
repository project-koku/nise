#
# Copyright 2022 Red Hat, Inc.
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
"""OCI Generator Unit Tests."""
from datetime import datetime
from datetime import timedelta
from unittest import TestCase
from unittest.mock import patch

from faker import Faker
from nise.generators.oci import OCIBlockStorageGenerator
from nise.generators.oci import OCIComputeGenerator
from nise.generators.oci import OCIDatabaseGenerator
from nise.generators.oci import OCIGenerator
from nise.generators.oci import OCINetworkGenerator
from nise.generators.oci.oci_generator import OCI_REPORT_TYPE_TO_COLS


class OCIGeneratorTestCase(TestCase):
    """Tests for OCI Generator."""

    def setUp(self):
        self.fake = Faker()
        self.attributes = None
        self.now = datetime.now().replace(microsecond=0, second=0, minute=0)
        self.one_hour = timedelta(minutes=60)
        self.one_day = timedelta(hours=24)
        self.currency = "USD"
        self.two_hours_ago = self.now - (2 * self.one_hour)
        self.six_hours_ago = self.now - (6 * self.one_hour)

    def test_timestamp_none(self):
        """Test the timestamp method fails with none."""
        with self.assertRaises(ValueError):
            OCIGenerator.timestamp(None)

    def test_timestamp_invalid(self):
        """Test timestamp method fails with an invalid date."""
        with self.assertRaises(ValueError):
            OCIGenerator.timestamp("invalid")

    def test_timestamp_valid(self):
        """Test timestamp method returns a date string."""
        generator = OCIGenerator(self.six_hours_ago, self.now, self.currency)
        tag_date = generator.timestamp(self.now)
        self.assertIsInstance(tag_date, str)
        self.assertEqual(tag_date, self.now.strftime("%Y-%m-%dT%H:%MZ"))

    def test_tag_timestamp(self):
        """Test tag timestamp method returns a string."""
        generator = OCIGenerator(self.six_hours_ago, self.now, self.currency)
        tag_date = generator._tag_timestamp(self.now)
        self.assertIsInstance(tag_date, str)

    def test_tag_timestamp_date(self):
        """Test tag timestamp method with valid date returns a timestamp."""
        generator = OCIGenerator(self.two_hours_ago, self.now, self.currency)
        date_str_format = "%Y-%m-%dT%H:%M:%S.000Z"
        self.assertEqual(generator._tag_timestamp(self.now), self.now.strftime(date_str_format))
        tag_date = datetime.strptime(generator._tag_timestamp(self.now), date_str_format)
        self.assertIsInstance(tag_date, datetime)

    def test_tag_timestamp_invalid_date(self):
        """Test tag timestamp method with invalid date returns an empty."""
        generator = OCIGenerator(self.six_hours_ago, self.now, self.currency)
        tag_date = generator._tag_timestamp("invalid date")
        self.assertIsInstance(tag_date, str)
        self.assertEqual(tag_date, "")

    def test_init_data_row(self):
        """Test the init data row method."""
        generator = OCIGenerator(self.six_hours_ago, self.now, self.currency)
        test_row = {}
        for report_type in OCI_REPORT_TYPE_TO_COLS:
            kwargs = {"report_type": report_type}
            test_row.update(generator._init_data_row(self.six_hours_ago, self.now, **kwargs))
            self.assertIsInstance(test_row, dict)

    def test_init_data_row_start_none(self):
        """Test the init data row method none start date."""
        generator = OCIGenerator(self.six_hours_ago, self.now, self.currency)
        with self.assertRaises(ValueError):
            generator._init_data_row(None, self.now)

    def test_init_data_row_end_none(self):
        """Test the init data row method none end date."""
        generator = OCIGenerator(self.six_hours_ago, self.now, self.currency)
        with self.assertRaises(ValueError):
            generator._init_data_row(self.six_hours_ago, None)

    def test_init_data_row_start_invalid(self):
        """Test the init data row method invalid start date."""
        generator = OCIGenerator(self.six_hours_ago, self.now, self.currency)
        with self.assertRaises(ValueError):
            generator._init_data_row("invalid", self.now)

    def test_init_data_row_end_invalid(self):
        """Test the init data row method invalid end date."""
        generator = OCIGenerator(self.six_hours_ago, self.now, self.currency)
        with self.assertRaises(ValueError):
            generator._init_data_row(self.six_hours_ago, "invalid")

    def test_add_common_usage_info(self):
        """Test that add_common_usage_info updates usage timestamps."""
        generator = OCIGenerator(self.six_hours_ago, self.now, self.currency)
        test_row_in = {}
        for report_type in OCI_REPORT_TYPE_TO_COLS:
            kwargs = {"report_type": report_type}
            test_row_in.update(generator._init_data_row(self.six_hours_ago, self.now, **kwargs))
            test_row_out = generator._add_common_usage_info(test_row_in, self.six_hours_ago, self.now)
            self.assertIn("lineItem/intervalUsageStart", test_row_out)
            self.assertIn("lineItem/intervalUsageEnd", test_row_out)

    def test_get_common_usage_data_update_tags(self):
        """Test that _get_common_usage_data updates tags."""
        tags = {"tags/free-form-tag": "discuss", "tags/orcl-cloud.free-tier-retained": "nice"}
        self.attributes = {"tags": tags}
        generator = OCIGenerator(self.six_hours_ago, self.now, self.currency, self.attributes)
        for _ in OCI_REPORT_TYPE_TO_COLS:
            result_usage_data = generator._get_common_usage_data(self.six_hours_ago, self.now)
            self.assertTrue(all(result_usage_data.get(key, None) == v for key, v in tags.items()))

    def test_generate_hourly_data(self):
        """Test that the _generate_hourly_data method is called."""
        kwargs = {}
        with patch.object(OCIGenerator, "_generate_hourly_data", return_value=None) as mock_method:
            generator = OCIGenerator(self.six_hours_ago, self.now, self.currency, self.attributes)
            generator._generate_hourly_data(**kwargs)
        mock_method.assert_called_with(**kwargs)

    @patch("nise.generators.oci.OCIGenerator.generate_data", autospec=True)
    def test_generate_data(self, mock_method):
        """Test that the generate_data method is called."""
        generator = OCIGenerator(self.six_hours_ago, self.now, self.currency, self.attributes)
        generator.generate_data()
        assert mock_method is OCIGenerator.generate_data
        assert mock_method.called


class TestOCIComputeGenerator(OCIGeneratorTestCase):
    """Tests for the Compute Generator."""

    def test_init_data_row(self):
        """Test the init data row."""
        generator = OCIComputeGenerator(self.six_hours_ago, self.now, self.currency)
        self.assertEqual(generator.service_name, "COMPUTE")

    def test_update_data(self):
        """Test that a compute row is updated."""
        generator = OCIComputeGenerator(self.six_hours_ago, self.now, self.currency, self.attributes)
        row = generator._update_data({}, self.six_hours_ago, self.now)
        self.assertEqual(row["product/service"], "COMPUTE")
        self.assertIsNotNone(row["product/resourceId"])
        self.assertIn("ocid1.instance.oci", row["product/resourceId"])

    def test_add_cost_data(self):
        """Test that cost data is added."""
        generator = OCIComputeGenerator(self.six_hours_ago, self.now, self.currency, self.attributes)
        row = generator._add_cost_data({}, self.six_hours_ago, self.now)
        self.assertEqual(row["cost/currencyCode"], self.currency)
        self.assertIn("B", row["cost/productSku"])
        self.assertEqual(len(row["cost/productSku"]), 6)

    def test_add_usage_data(self):
        """Test that usage data is added."""
        generator = OCIComputeGenerator(self.six_hours_ago, self.now, self.currency, self.attributes)
        usage_row = generator._add_usage_data({}, self.six_hours_ago, self.now)
        self.assertIsInstance(usage_row["usage/consumedQuantity"], int)
        self.assertIsInstance(usage_row["usage/billedQuantity"], int)
        self.assertIsInstance(usage_row["usage/consumedQuantityUnits"], str)
        self.assertIsInstance(usage_row["usage/consumedQuantityMeasure"], str)

    def test_generate_data(self):
        """Test that the generate_data method for network service works."""
        generator = OCIComputeGenerator(self.six_hours_ago, self.now, self.currency, self.attributes)
        with patch.object(generator, "_generate_hourly_data") as mock_method:
            kwargs = {}
            generator.generate_data(**kwargs)
            mock_method.assert_called_with(**kwargs)


class TestOCINetworkGenerator(OCIGeneratorTestCase):
    """Tests for the Network Generator."""

    def test_init_data_row(self):
        """Test the init data row."""
        generator = OCINetworkGenerator(self.six_hours_ago, self.now, self.currency, self.attributes)
        self.assertEqual(generator.service_name, "NETWORK")

    def test_update_data(self):
        """Test that a network row is updated."""
        generator = OCINetworkGenerator(self.six_hours_ago, self.now, self.currency, self.attributes)
        row = generator._update_data({}, self.six_hours_ago, self.now)
        self.assertEqual(row["product/service"], "NETWORK")
        self.assertIsNotNone(row["product/resourceId"])

    def test_add_cost_data(self):
        """Test that cost data is added."""
        generator = OCINetworkGenerator(self.six_hours_ago, self.now, self.currency, self.attributes)
        row = generator._add_cost_data({}, self.six_hours_ago, self.now)
        self.assertEqual(row["cost/currencyCode"], self.currency)
        self.assertIn("B", row["cost/productSku"])

    def test_add_usage_data(self):
        """Test that usage specific data for network service is added."""
        generator = OCINetworkGenerator(self.six_hours_ago, self.now, self.currency, self.attributes)
        usage_row = generator._add_usage_data({}, self.six_hours_ago, self.now)
        self.assertIsInstance(usage_row["usage/consumedQuantity"], int)
        self.assertIsInstance(usage_row["usage/billedQuantity"], int)
        self.assertIsInstance(usage_row["usage/consumedQuantityUnits"], str)
        self.assertIsInstance(usage_row["usage/consumedQuantityMeasure"], str)


class TestOCIBlockStorageGenerator(OCIGeneratorTestCase):
    """Tests for the Block Storage Generator."""

    def test_init_data_row(self):
        """Test the init data row for block storage data."""
        generator = OCIBlockStorageGenerator(self.six_hours_ago, self.now, self.currency, self.attributes)
        self.assertEqual(generator.service_name, "BLOCK_STORAGE")

    def test_update_data(self):
        """Test that a block storage data row is updated."""
        generator = OCIBlockStorageGenerator(self.six_hours_ago, self.now, self.currency, self.attributes)
        row = generator._update_data({}, self.six_hours_ago, self.now)
        self.assertEqual(row["product/service"], "BLOCK_STORAGE")
        self.assertEqual(row["product/service"], generator.service_name)
        self.assertIsNotNone(row["product/resourceId"])
        self.assertIn("ocid1.bootvolume.oc1", row["product/resourceId"])

    def test_add_cost_data(self):
        """Test that cost specific data for block storage service is added."""
        generator = OCIBlockStorageGenerator(self.six_hours_ago, self.now, self.currency, self.attributes)
        test_row = generator._add_cost_data({}, self.six_hours_ago, self.now)
        self.assertEqual(test_row["cost/currencyCode"], self.currency)
        self.assertIn("B", test_row["cost/productSku"])

    def test_add_usage_data(self):
        """Test that usage specific data for block storage service is added."""
        generator = OCIBlockStorageGenerator(self.six_hours_ago, self.now, self.currency, self.attributes)
        test_row = generator._add_usage_data({}, self.six_hours_ago, self.now)
        self.assertIsInstance(test_row["usage/consumedQuantity"], int)
        self.assertIsInstance(test_row["usage/billedQuantity"], int)
        self.assertIsInstance(test_row["usage/consumedQuantityUnits"], str)
        self.assertIsInstance(test_row["usage/consumedQuantityMeasure"], str)


class TestOCIDatabaseGenerator(OCIGeneratorTestCase):
    """Tests for the Database Generator."""

    def test_init_data_row(self):
        """Test the init data row for database generator is created."""
        generator = OCIDatabaseGenerator(self.two_hours_ago, self.now, self.currency, self.attributes)
        self.assertEqual(generator.service_name, "DATABASE")

    def test_update_data(self):
        """Test that a database data row is updated."""
        generator = OCIDatabaseGenerator(self.six_hours_ago, self.now, self.currency, self.attributes)
        row = generator._update_data({}, self.six_hours_ago, self.now)
        self.assertEqual(row["product/service"], "DATABASE")
        self.assertEqual(row["product/service"], generator.service_name)
        self.assertIsNotNone(row["product/resourceId"])

    def test_add_cost_data(self):
        """Test that cost specific data for database service is added."""
        generator = OCIDatabaseGenerator(self.two_hours_ago, self.now, self.currency, self.attributes)
        test_row = generator._add_cost_data({}, self.two_hours_ago, self.now)
        self.assertEqual(test_row["cost/currencyCode"], self.currency)
        self.assertIn("B", test_row["cost/productSku"])

    def test_add_usage_data(self):
        """Test that usage specific data for database service is added."""
        generator = OCIDatabaseGenerator(self.two_hours_ago, self.now, self.currency, self.attributes)
        test_row = generator._add_usage_data({}, self.two_hours_ago, self.now)
        self.assertIsInstance(test_row["usage/consumedQuantity"], int)
        self.assertIsInstance(test_row["usage/billedQuantity"], int)
        self.assertIsInstance(test_row["usage/consumedQuantityUnits"], str)
        self.assertIsInstance(test_row["usage/consumedQuantityMeasure"], str)
