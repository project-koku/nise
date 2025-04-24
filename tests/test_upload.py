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
from unittest.mock import Mock
from unittest.mock import patch

import boto3
import faker
from botocore.exceptions import ClientError
from google.cloud.exceptions import GoogleCloudError
from nise.upload import BlobServiceClient
from nise.upload import gcp_bucket_to_dataset
from nise.upload import upload_to_azure_container
from nise.upload import upload_to_gcp_storage
from nise.upload import upload_to_s3


fake = faker.Faker()


class UploadTestCase(TestCase):
    """
    TestCase class for upload
    """

    @patch("boto3.resource")
    def test_upload_to_s3_success(self, mock_boto_resource):
        """Test upload_to_s3 method with mock s3."""
        bucket_name = "my_bucket"
        s3_client = Mock()
        s3_client.Bucket.create.return_value = Mock()
        s3_client.Bucket.return_value.upload_file.return_value = Mock()
        mock_boto_resource.return_value = s3_client
        s3_client = boto3.resource("s3")
        s3_client.Bucket(bucket_name).create()
        with NamedTemporaryFile(delete=False) as t_file:
            success = upload_to_s3(bucket_name, "/file.txt", t_file.name)
        self.assertTrue(success)
        os.remove(t_file.name)

    @patch("boto3.resource")
    def test_upload_to_s3_failure(self, mock_boto_resource):
        """Test upload_to_s3 method with mock s3."""
        bucket_name = "my_bucket"
        s3_client = Mock()
        s3_client.Bucket.create.return_value = Mock()
        s3_client.Bucket.return_value.upload_file.side_effect = ClientError({"Error": {}}, "Create")
        mock_boto_resource.return_value = s3_client
        s3_client = boto3.resource("s3")
        s3_client.Bucket(bucket_name).create()
        with NamedTemporaryFile(delete=False) as t_file:
            success = upload_to_s3(bucket_name, "/file.txt", t_file.name)
        self.assertFalse(success)
        os.remove(t_file.name)

    @patch.object(BlobServiceClient, "from_connection_string")
    def test_upload_to_azure_success(self, _):
        """Test successful upload_to_storage method with mock."""
        container_name = "my_container"
        with NamedTemporaryFile(delete=False) as t_file:
            success = upload_to_azure_container(container_name, t_file.name, "/file.txt")
        self.assertTrue(success)
        os.remove(t_file.name)

    @patch.object(BlobServiceClient, "from_connection_string")
    def test_upload_to_azure_failure(self, mock_blob_service):
        """Test failure upload_to_storage method with mock."""
        mock_blob_service.side_effect = IOError
        container_name = "my_container"
        with NamedTemporaryFile(delete=False) as t_file:
            success = upload_to_azure_container(container_name, t_file.name, "/file.txt")
        self.assertFalse(success)
        os.remove(t_file.name)

    @patch.dict(os.environ, {"GOOGLE_APPLICATION_CREDENTIALS": "/path/to/creds"})
    @patch("nise.upload.storage")
    def test_gcp_upload_success(self, mock_storage):
        """Test upload_to_s3 method with mock s3."""
        bucket_name = fake.slug()
        local_path = fake.file_path()
        remote_path = fake.file_path()
        uploaded = upload_to_gcp_storage(bucket_name, local_path, remote_path)

        mock_client = mock_storage.Client.return_value
        mock_client.get_bucket.assert_called_with(bucket_name)

        mock_bucket = mock_client.get_bucket.return_value
        mock_bucket.blob.assert_called_with(remote_path)

        mock_blob = mock_bucket.blob.return_value
        mock_blob.upload_from_filename.assert_called_with(local_path)

        self.assertTrue(uploaded)

    @patch.dict(os.environ, {"GOOGLE_APPLICATION_CREDENTIALS": "/path/to/creds"})
    @patch("nise.upload.storage.Client")
    def test_gcp_upload_error(self, mock_storage):
        """Test upload_to_s3 method with mock s3."""
        gcp_client = mock_storage.return_value
        gcp_client.get_bucket.side_effect = GoogleCloudError("GCP Error")

        bucket_name = fake.slug()
        local_path = fake.file_path()
        remote_path = fake.file_path()
        uploaded = upload_to_gcp_storage(bucket_name, local_path, remote_path)

        self.assertFalse(uploaded)

    def test_gcp_upload_fail_no_credentials(self):
        """Test upload_to_s3 method with mock s3."""
        bucket_name = fake.slug()
        local_path = fake.file_path()
        remote_path = fake.file_path()
        uploaded = upload_to_gcp_storage(bucket_name, local_path, remote_path)

        self.assertFalse(uploaded)

    @patch.dict(os.environ, {"GOOGLE_APPLICATION_CREDENTIALS": "/path/to/creds"})
    @patch("nise.upload.bigquery")
    @patch("nise.upload.storage")
    def test_gcp_bucket_to_dataset(self, mock_storage, mock_bigquery):
        """Test creation of bigquery dataset from file in gcp storage"""
        bucket_name = fake.slug()
        local_path = fake.file_path()
        dataset_name = fake.slug()
        table_name = fake.slug()

        uploaded = gcp_bucket_to_dataset(bucket_name, local_path, dataset_name, table_name)

        mock_client = mock_bigquery.Client.return_value
        mock_job_config = mock_bigquery.LoadJobConfig.return_value

        mock_client.create_dataset.assert_called_once()

        uri = f"gs://{bucket_name}/{local_path}"
        table_id = f"{mock_client.project}.{dataset_name}.{table_name}"
        mock_client.load_table_from_uri.assert_called_with(uri, table_id, job_config=mock_job_config)

        self.assertTrue(uploaded)

    @patch.dict(os.environ, {"GOOGLE_APPLICATION_CREDENTIALS": "/path/to/creds"})
    @patch("nise.upload.bigquery")
    @patch("nise.upload.storage")
    def test_gcp_w_resources_bucket_to_dataset(self, mock_storage, mock_bigquery):
        """Test creation of bigquery dataset from file in gcp storage"""
        bucket_name = fake.slug()
        local_path = fake.file_path()
        dataset_name = fake.slug()
        table_name = fake.slug()

        uploaded = gcp_bucket_to_dataset(bucket_name, local_path, dataset_name, table_name, resource_level=True)

        mock_client = mock_bigquery.Client.return_value
        mock_job_config = mock_bigquery.LoadJobConfig.return_value

        mock_client.create_dataset.assert_called_once()

        uri = f"gs://{bucket_name}/{local_path}"
        table_id = f"{mock_client.project}.{dataset_name}.{table_name}"
        mock_client.load_table_from_uri.assert_called_with(uri, table_id, job_config=mock_job_config)

        self.assertTrue(uploaded)

    @patch.dict(os.environ, {"GOOGLE_APPLICATION_CREDENTIALS": "/path/to/creds"})
    @patch("nise.upload.bigquery")
    @patch("nise.upload.storage")
    def test_gcp_w_daily_flow_bucket_to_dataset(self, mock_storage, mock_bigquery):
        """Test creation of bigquery dataset from file in gcp storage"""
        bucket_name = fake.slug()
        local_path = fake.file_path()
        dataset_name = fake.slug()
        table_name = fake.slug()

        uploaded = gcp_bucket_to_dataset(bucket_name, local_path, dataset_name, table_name, gcp_daily_flow=True)

        self.assertTrue(uploaded)

    def test_gcp_dataset_fail_no_credentials(self):
        """Test bucket_to_dataset method fails with no credentials."""
        bucket_name = fake.slug()
        local_path = fake.file_path()
        dataset_name = fake.slug()
        table_name = fake.slug()

        uploaded = gcp_bucket_to_dataset(bucket_name, local_path, dataset_name, table_name)

        self.assertFalse(uploaded)
