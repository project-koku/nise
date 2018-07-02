#
# Copyright 2018 Red Hat, Inc.
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
from datetime import datetime, timedelta
from unittest import TestCase

from faker import Faker

from nise.generators.generator import AbstractGenerator, COLUMNS


class TestGenerator(AbstractGenerator):

    def _update_data(self, row, start, end):
        return None

    def generate_data(self):
        return []


class AbstractGeneratorTestCase(TestCase):
    """
    TestCase class for Abstract Generator
    """

    def setUp(self):
        self.fake = Faker()
        self.now = datetime.now().replace(microsecond=0, second=0, minute=0)
        self.one_hour = timedelta(minutes=60)
        self.payer_account = self.fake.ean(length=13)
        self.usage_accounts = (self.payer_account,
                               self.fake.ean(length=13),
                               self.fake.ean(length=13),
                               self.fake.ean(length=13),
                               self.fake.ean(length=13))

    def test_set_hours_invalid_start(self):
        """Test that the start date must be a date object."""
        with self.assertRaises(ValueError):
            TestGenerator('invalid', self.now,
                          self.payer_account, self.usage_accounts)

    def test_set_hours_invalid_end(self):
        """Test that the end date must be a date object."""
        with self.assertRaises(ValueError):
            TestGenerator(self.now, 'invalid',
                          self.payer_account, self.usage_accounts)

    def test_set_hours_none_start(self):
        """Test that the start date is not None."""
        with self.assertRaises(ValueError):
            TestGenerator(None, self.now,
                          self.payer_account, self.usage_accounts)

    def test_set_hours_none_end(self):
        """Test that the end date is not None."""
        with self.assertRaises(ValueError):
            TestGenerator(self.now, None,
                          self.payer_account, self.usage_accounts)

    def test_set_hours_compared_dates(self):
        """Test that the start date must be less than the end date."""
        hour_ago = self.now - self.one_hour
        with self.assertRaises(ValueError):
            TestGenerator(self. now, hour_ago,
                          self.payer_account, self.usage_accounts)

    def test_set_hours(self):
        """Test that a valid list of hours are returned."""
        two_hours_ago = (self.now - self.one_hour) - self.one_hour
        generator = TestGenerator(two_hours_ago, self.now,
                                  self.payer_account, self.usage_accounts)
        expected = [{'start': two_hours_ago,
                     'end': two_hours_ago + self.one_hour}]
        self.assertEqual(generator.hours, expected)

    def test_timestamp_none(self):
        """Test that the timestamp method fails with None."""
        with self.assertRaises(ValueError):
            TestGenerator.timestamp(None)

    def test_timestamp_invalid(self):
        """Test that the timestamp method fails with an not a date."""
        with self.assertRaises(ValueError):
            TestGenerator.timestamp('invalid')

    def test_init_data_row(self):
        """Test the init data row method."""
        two_hours_ago = (self.now - self.one_hour) - self.one_hour
        generator = TestGenerator(two_hours_ago, self.now,
                                  self.payer_account, self.usage_accounts)
        a_row = generator._init_data_row(two_hours_ago, self.now)
        self.assertIsInstance(a_row, dict)
        for col in COLUMNS:
            self.assertIsNotNone(a_row.get(col))

    def test_init_data_row_start_none(self):
        """Test the init data row method none start date."""
        two_hours_ago = (self.now - self.one_hour) - self.one_hour
        generator = TestGenerator(two_hours_ago, self.now,
                                  self.payer_account, self.usage_accounts)
        with self.assertRaises(ValueError):
            generator._init_data_row(None, self.now)

    def test_init_data_row_end_none(self):
        """Test the init data row method none end date."""
        two_hours_ago = (self.now - self.one_hour) - self.one_hour
        generator = TestGenerator(two_hours_ago, self.now,
                                  self.payer_account, self.usage_accounts)
        with self.assertRaises(ValueError):
            generator._init_data_row(two_hours_ago, None)

    def test_init_data_row_start_invalid(self):
        """Test the init data row method invalid start date."""
        two_hours_ago = (self.now - self.one_hour) - self.one_hour
        generator = TestGenerator(two_hours_ago, self.now,
                                  self.payer_account, self.usage_accounts)
        with self.assertRaises(ValueError):
            generator._init_data_row('invalid', self.now)

    def test_init_data_row_end_invalid(self):
        """Test the init data row method invalid end date."""
        two_hours_ago = (self.now - self.one_hour) - self.one_hour
        generator = TestGenerator(two_hours_ago, self.now,
                                  self.payer_account, self.usage_accounts)
        with self.assertRaises(ValueError):
            generator._init_data_row(two_hours_ago, 'invalid')
