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
import os
import mock
from tempfile import NamedTemporaryFile
from unittest import TestCase

import boto3

from nise.upload import upload_to_s3


class UploadTestCase(TestCase):
    """
    TestCase class for upload
    """

    @mock.patch('boto3.resource')
    def test_upload_success(self, mock_boto_resource):
        """Test upload_to_s3 method with mock s3."""
        bucket_name = 'my_bucket'
        s3_client = mock.Mock()
        s3_client.Bucket.create.return_value = mock.Mock()
        s3_client.Bucket.upload_file.return_value = mock.Mock()
        mock_boto_resource.return_value = s3_client
        s3_client = boto3.resource('s3')
        bucket = s3_client.Bucket(bucket_name).create()
        t_file = NamedTemporaryFile(delete=False)
        success = upload_to_s3(bucket_name, '/file.txt', t_file.name)
        self.assertTrue(success)
        os.remove(t_file.name)
