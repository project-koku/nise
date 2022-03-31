from faker import Faker
from datetime import datetime
from datetime import timedelta
from unittest import TestCase
from nise.generators.oci import OCIGenerator
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
        """Test that the timestamp method fails with None."""
        with self.assertRaises(ValueError):
            TestGenerator.timestamp(None)

    def test_timestamp_invalid(self):
        """Test that the timestamp method fails with an not a date."""
        with self.assertRaises(ValueError):
            TestGenerator.timestamp("invalid")

    def test_init_data_row(self):
        """Test the init data row method."""
        generator = TestGenerator(self.six_hours_ago, self.now, self.currency)
        for report_type in OCI_REPORT_TYPE_TO_COLS:
            kwargs = {"report_type":report_type}
            a_row = generator._init_data_row(self.six_hours_ago, self.now, **kwargs)
            self.assertIsInstance(a_row, dict)
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
    # def test_init_data_row_start_none(self):
    #     """Test the init data row method none start date."""
    #     two_hours_ago = (self.now - self.one_hour) - self.one_hour
    #     generator = TestGenerator(two_hours_ago, self.now, self.currency, self.payer_account, self.usage_accounts)
    #     with self.assertRaises(ValueError):
    #         generator._init_data_row(None, self.now)

    # def test_init_data_row_end_none(self):
    #     """Test the init data row method none end date."""
    #     two_hours_ago = (self.now - self.one_hour) - self.one_hour
    #     generator = TestGenerator(two_hours_ago, self.now, self.currency, self.payer_account, self.usage_accounts)
    #     with self.assertRaises(ValueError):
    #         generator._init_data_row(two_hours_ago, None)

    # def test_init_data_row_start_invalid(self):
    #     """Test the init data row method invalid start date."""
    #     two_hours_ago = (self.now - self.one_hour) - self.one_hour
    #     generator = TestGenerator(two_hours_ago, self.now, self.currency, self.payer_account, self.usage_accounts)
    #     with self.assertRaises(ValueError):
    #         generator._init_data_row("invalid", self.now)

    # def test_init_data_row_end_invalid(self):
    #     """Test the init data row method invalid end date."""
    #     two_hours_ago = (self.now - self.one_hour) - self.one_hour
    #     generator = TestGenerator(two_hours_ago, self.now, self.currency, self.payer_account, self.usage_accounts)
    #     with self.assertRaises(ValueError):
    #         generator._init_data_row(two_hours_ago, "invalid")

   