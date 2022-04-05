from faker import Faker
from datetime import datetime
from datetime import timedelta
from unittest import TestCase
from unittest.mock import Mock, MagicMock
from nise.generators.oci import OCIGenerator
from nise.generators.oci import OCIComputeGenerator
from nise.generators.oci.oci_generator import OCI_COST_REPORT
from nise.generators.oci.oci_generator import OCI_USAGE_REPORT
from nise.generators.oci.oci_generator import OCI_REPORT_TYPE_TO_COLS


class TestGenerator(OCIGenerator):
    def _update_data(self, row, start, end):
        return None

    def generate_data(self, report_type=None):
        return []

class OCIGeneratorTestCase(TestCase):
    """Tests for OCI Generator."""
    def setUp(self):
        self.fake = Faker()
        self.attributes = None
        self.now = datetime.now().replace(microsecond=0, second=0, minute=0)
        self.one_hour = timedelta(minutes=60)
        self.one_day = timedelta(hours=24)
        self.currency = "USD"
        self.six_hours_ago = self.now - (6 * self.one_hour)

    def test_timestamp_none(self):
        """Test the timestamp method fails with none."""
        with self.assertRaises(ValueError):
            TestGenerator.timestamp(None)

    def test_timestamp_invalid(self):
        """Test timestamp method fails with an invalid date."""
        with self.assertRaises(ValueError):
            TestGenerator.timestamp("invalid")
    
    def test_tag_timestamp(self):
        """Test tag timestamp method returns a string."""
        generator = TestGenerator(self.six_hours_ago, self.now, self.currency)
        test_date = datetime.now()
        tag_date = generator._tag_timestamp(test_date)
        self.assertIsInstance(tag_date, str)
    
    def test_tag_timestamp_date(self):
        """Test tag timestamp method with valid date returns a timestamp."""
        generator = TestGenerator(self.six_hours_ago, self.now, self.currency)
        test_date = datetime.now()
        tag_date = datetime.strptime(
            generator._tag_timestamp(test_date), 
            "%Y-%m-%dT%H:%M:%S.000Z"
        )
        self.assertIsInstance(tag_date, datetime) 
    
    def test_tag_timestamp_invalid_date(self):
        """Test tag timestamp method with invalid date returns an empty."""
        generator = TestGenerator(self.six_hours_ago, self.now, self.currency)
        tag_date = generator._tag_timestamp('invalid date')
        self.assertIsInstance(tag_date, str)
        self.assertEqual(tag_date, "")

    def test_init_data_row(self):
        """Test the init data row method."""
        generator = TestGenerator(self.six_hours_ago, self.now, self.currency)
        test_row = {}
        for report_type in OCI_REPORT_TYPE_TO_COLS:
            kwargs = {"report_type":report_type}
            test_row.update(generator._init_data_row(self.six_hours_ago, self.now, **kwargs))
            self.assertIsInstance(test_row, dict)

    def test_init_data_row_start_none(self):
        """Test the init data row method none start date."""
        generator = TestGenerator(self.six_hours_ago, self.now, self.currency)
        with self.assertRaises(ValueError):
            generator._init_data_row(None, self.now)
        
    def test_init_data_row_end_none(self):
        """Test the init data row method none end date."""
        generator = TestGenerator(self.six_hours_ago, self.now, self.currency)
        with self.assertRaises(ValueError):
            generator._init_data_row(self.six_hours_ago, None)

    def test_init_data_row_start_invalid(self):
        """Test the init data row method invalid start date."""
        generator = TestGenerator(self.six_hours_ago, self.now, self.currency)
        with self.assertRaises(ValueError):
            generator._init_data_row("invalid", self.now)

    def test_init_data_row_end_invalid(self):
        """Test the init data row method invalid end date."""
        generator = TestGenerator(self.six_hours_ago, self.now, self.currency)
        with self.assertRaises(ValueError):
            generator._init_data_row(self.six_hours_ago, "invalid")
    
    def test_add_common_usage_info(self):
        """Test that add_common_usage_info updates usage timestamps."""
        generator = TestGenerator(self.six_hours_ago, self.now, self.currency)
        test_row_in = {}
        for report_type in OCI_REPORT_TYPE_TO_COLS:
            kwargs = {"report_type":report_type}
            test_row_in.update(generator._init_data_row(self.six_hours_ago, self.now, **kwargs))
        test_row_out = generator._add_common_usage_info(test_row_in, self.six_hours_ago, self.now)
        self.assertIn("lineItem/intervalUsageStart", test_row_out)
        self.assertIn("lineItem/intervalUsageEnd", test_row_out)

    # def test_generate_hourly_data_(self):
    #     # TODO:
    #     """Test that generate_hourly_data calls the test method."""
    #     generator = TestGenerator(self.six_hours_ago, self.now, self.currency)        
    #     kwargs = {"report_type": "oci_cost_report"}        
    #     mock_oci_generator = MagicMock()
    #     _return_value = generator._generate_hourly_data(**kwargs)
    #     mock_oci_generator._generate_hourly_data.return_value = _return_value
    #     test_return = mock_oci_generator._generate_hourly_data(**kwargs)
    #     mock_oci_generator._generate_hourly_data.assert_called_with(**kwargs)
    #     self.assertEqual(test_return, _return_value)


class TestOCIComputeGenerator(OCIGeneratorTestCase):
    """Tests for the Compute Generator type."""

    def test_init_data_row(self):
        """Test the init data row."""
        for report_type in OCI_REPORT_TYPE_TO_COLS:
            generator = OCIComputeGenerator(
                self.six_hours_ago, self.now, self.currency, report_type
            )
            self.assertEqual(generator.service_name, "COMPUTE")
            self.assertEqual(generator.report_type, report_type)
            self.assertIsNotNone(generator.report_type)

    def test_init_data_with_none_report(self):
        """Test the init data with a none report type."""
        generator = OCIComputeGenerator(self.six_hours_ago, self.now, self.currency, None)
        self.assertIsNone(generator.report_type)

    def test_update_data(self):
        """Test that row is updated."""
        generator = OCIComputeGenerator(self.six_hours_ago, self.now, self.currency, None, self.attributes)
        row = generator._update_data({}, self.six_hours_ago, self.now)
        self.assertEqual(row["product/service"], "COMPUTE")
        self.assertIsNotNone(row["product/resourceId"])
        self.assertIn("ocid1.instance.oci", row["product/resourceId"])

    def test_add_cost_data(self):
        """Test that cost specific data is added."""
        report_type = "oci_cost_report"
        generator = OCIComputeGenerator(self.six_hours_ago, self.now, self.currency, report_type, self.attributes)
        row = generator._add_cost_data({}, self.six_hours_ago, self.now)
        self.assertEqual(row["cost/currencyCode"], self.currency)
        self.assertIn("B", row["cost/productSku"])
        self.assertEqual(len(row["cost/productSku"]), 6)
    
    def test_add_usage_data(self):
        """Test that usage specific data is added."""
        report_type = "oci_usage_report"
        generator = OCIComputeGenerator(self.six_hours_ago, self.now, self.currency, report_type, self.attributes)
        usage_row = generator._add_usage_data({}, self.six_hours_ago, self.now)
        self.assertIsInstance(usage_row["usage/consumedQuantity"], int)
        self.assertIsInstance(usage_row["usage/billedQuantity"], int)
        self.assertIsInstance(usage_row["usage/consumedQuantityUnits"], str)
        self.assertIsInstance(usage_row["usage/consumedQuantityMeasure"], str)
        self.assertNotEqual(usage_row["usage/consumedQuantityUnits"], "")

    def test_generate_data(self):
        """Test that the OCI COMPUTE generate_data method works."""
        for report_type in OCI_REPORT_TYPE_TO_COLS:
            generator = OCIComputeGenerator(self.six_hours_ago, self.now, self.currency, report_type)
            data = generator.generate_data()
            self.assertNotEqual(data, [])
    
    def test_generate_data_report_type_none(self):
        # TODO: use mock to check if functions are called
        """Test that the OCI COMPUTE generate_data method returns empty list with none report type."""
        # for report_type in OCI_REPORT_TYPE_TO_COLS:
        generator = OCIComputeGenerator(self.six_hours_ago, self.now, self.currency, None)
        data = generator.generate_data()
        self.assertEqual(data, [])