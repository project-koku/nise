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
import datetime
import os
import shutil

from tempfile import (mkdtemp, NamedTemporaryFile)

from unittest import TestCase
from unittest.mock import ANY, patch

from moto import mock_s3

from nise.report import create_report, _write_csv, _write_manifest


class ReportTestCase(TestCase):
    """
    TestCase class for report functions
    """

    def test_write_csv(self):
        """Test the writing of the CSV data."""
        temp_file = NamedTemporaryFile(mode='w', delete=False)
        headers = ['col1', 'col2']
        data = [{'col1': 'r1c1', 'col2': 'r1c2'},
                {'col1': 'r2c1', 'col2': 'r2c2'}]
        _write_csv(temp_file, data, headers)
        self.assertTrue(os.path.exists(temp_file.name))
        os.remove(temp_file.name)

    def test_write_manifest(self):
        """Test the writing of the manifest data."""
        data = '[{"col1": "r1c1", "col2": "r1c2"},' \
               '{"col1": "r2c1", "col2": "r2c2"}]'
        manifest_path = _write_manifest(data)
        self.assertTrue(os.path.exists(manifest_path))
        os.remove(manifest_path)

    @patch('nise.report._write_csv')
    def test_create_report_no_s3(self, write_csv):
        """Test the report creation method no s3."""
        temp_file = NamedTemporaryFile()
        now = datetime.datetime.now().replace(microsecond=0, second=0, minute=0)
        one_day = datetime.timedelta(days=1)
        yesterday = now - one_day
        create_report(temp_file, {'start_date': yesterday, 'end_date': now})
        write_csv.assert_called_once_with(ANY, ANY)

    @mock_s3
    @patch('nise.report._write_csv')
    def test_create_report_with_s3(self, write_csv):
        """Test the report creation method with s3."""
        temp_file = NamedTemporaryFile()
        now = datetime.datetime.now().replace(microsecond=0, second=0, minute=0)
        one_day = datetime.timedelta(days=1)
        yesterday = now - one_day
        options = {'start_date': yesterday,
                   'end_date': now,
                   'bucket_name': 'my_bucket',
                   'report_name': 'cur_report'}
        create_report(temp_file, options)
        write_csv.assert_called_once_with(ANY, ANY)

    @patch('nise.report._write_csv')
    def test_create_report_with_local_dir(self, write_csv):
        """Test the report creation method with local directory."""
        temp_file = NamedTemporaryFile()
        now = datetime.datetime.now().replace(microsecond=0, second=0, minute=0)
        one_day = datetime.timedelta(days=1)
        yesterday = now - one_day
        local_bucket_path = mkdtemp()
        options = {'start_date': yesterday,
                   'end_date': now,
                   'bucket_name': local_bucket_path,
                   'report_name': 'cur_report'}
        create_report(temp_file, options)
        write_csv.assert_called_once_with(ANY, ANY)
        shutil.rmtree(local_bucket_path)
