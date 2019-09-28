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
from tempfile import NamedTemporaryFile
from unittest import TestCase
from unittest.mock import Mock, patch

import boto3
from azure.storage.blob import BlockBlobService
from botocore.exceptions import ClientError

from nise.upload import upload_to_s3, upload_to_storage


class UploadTestCase(TestCase):
    """
    TestCase class for upload
    """

    @patch('boto3.resource')
    def test_upload_to_s3_success(self, mock_boto_resource):
        """Test upload_to_s3 method with mock s3."""
        bucket_name = 'my_bucket'
        s3_client = Mock()
        s3_client.Bucket.create.return_value = Mock()
        s3_client.Bucket.return_value.upload_file.return_value = Mock()
        mock_boto_resource.return_value = s3_client
        s3_client = boto3.resource('s3')
        s3_client.Bucket(bucket_name).create()
        t_file = NamedTemporaryFile(delete=False)
        success = upload_to_s3(bucket_name, '/file.txt', t_file.name)
        self.assertTrue(success)
        os.remove(t_file.name)

    @patch('boto3.resource')
    def test_upload_to_s3_failure(self, mock_boto_resource):
        """Test upload_to_s3 method with mock s3."""
        bucket_name = 'my_bucket'
        s3_client = Mock()
        s3_client.Bucket.create.return_value = Mock()
        s3_client.Bucket.return_value.upload_file.side_effect = ClientError({'Error': {}}, 'Create')
        mock_boto_resource.return_value = s3_client
        s3_client = boto3.resource('s3')
        s3_client.Bucket(bucket_name).create()
        t_file = NamedTemporaryFile(delete=False)
        success = upload_to_s3(bucket_name, '/file.txt', t_file.name)
        self.assertFalse(success)
        os.remove(t_file.name)

    @patch.object(BlockBlobService, 'create_blob_from_path')
    def test_upload_to_azure_success(self, mock_blob_service):
        """Test upload_to_s3 method with mock s3."""
        container_name = 'my_container'
        t_file = NamedTemporaryFile(delete=False)
        success = upload_to_storage(container_name, '/file.txt', t_file.name)
        self.assertTrue(success)
        os.remove(t_file.name)

    @patch.object(BlockBlobService, 'create_blob_from_path')
    def test_upload_to_azure_failure(self, mock_blob_service):
        """Test upload_to_s3 method with mock s3."""
        mock_blob_service.side_effect = Exception({'Error': {}}, 'Create')
        container_name = 'my_container'
        t_file = NamedTemporaryFile(delete=False)
        success = upload_to_storage(container_name, '/file.txt', t_file.name)
        self.assertFalse(success)
        os.remove(t_file.name)
