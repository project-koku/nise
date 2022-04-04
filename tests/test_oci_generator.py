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

class TestOCIGenerator(TestCase):
    """Tests for OCI Generator."""
    def setUp(self):
        self.fake = Faker()
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