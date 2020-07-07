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
"""Defines the upload mechanism to various clouds."""
import os
import sys
import traceback

import boto3
from azure.storage.blob import BlobServiceClient
from botocore.exceptions import ClientError
from google.cloud import storage
from google.cloud.exceptions import GoogleCloudError
from msrestazure.azure_exceptions import ClientException
from msrestazure.azure_exceptions import CloudError
from nise.util import LOG
from requests.exceptions import ConnectionError as BotoConnectionError


def upload_to_s3(bucket_name, bucket_file_path, local_path):
    """Upload data to an S3 bucket.

    Args:
        bucket_name (String): The name of the S3 bucket
        bucket_file_path (String): The path to store the file to
        local_path  (String): The local file system path of the file
    Returns:
        (Boolean): True if file was uploaded

    """
    uploaded = True
    try:
        s3_client = boto3.resource("s3")
        s3_client.Bucket(bucket_name).upload_file(local_path, bucket_file_path)
        msg = f"Uploaded {bucket_file_path} to s3 bucket {bucket_name}."
        LOG.info(msg)
    except (ClientError, BotoConnectionError, boto3.exceptions.S3UploadFailedError) as upload_err:
        LOG.error(upload_err)
        uploaded = False
    return uploaded


def upload_to_azure_container(storage_file_name, local_path, storage_file_path):
    """Upload data to a storage account.

    Args:
        storage_file_name (String): The container to upload file to
        local_path  (String): The full local file system path of the file
        storage_file_path (String): The file path to upload to within container

    Returns:
        (Boolean): True if file was uploaded

    """
    try:
        # Retrieve the connection string for use with the application.
        connect_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        blob_client = blob_service_client.get_blob_client(container=storage_file_name, blob=storage_file_path)
        with open(local_path, "rb") as data:
            blob_client.upload_blob(data=data)
        LOG.info(f"uploaded {storage_file_name} to {storage_file_path}")
    except (CloudError, ClientException, IOError) as error:
        LOG.error(error)
        traceback.print_exc(file=sys.stderr)
        return False
    return True


def upload_to_gcp_storage(bucket_name, source_file_name, destination_blob_name):
    """
    Upload data to a GCP Storage Bucket.

    Args:
        bucket_name (String): The container to upload file to
        source_file_name  (String): The full local file system path of the file
        destination_blob_name (String): Destination blob name to store in GCP.

    Returns:
        (Boolean): True if file was uploaded

    """
    uploaded = True

    if "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ:
        LOG.warning(
            "Please set your GOOGLE_APPLICATION_CREDENTIALS "
            "environment variable before attempting to load file into"
            "GCP Storage."
        )
        return False
    try:
        storage_client = storage.Client()

        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)

        blob.upload_from_filename(source_file_name)

        LOG.info(f"File {source_file_name} uploaded to GCP Storage {destination_blob_name}.")
    except GoogleCloudError as upload_err:
        LOG.error(upload_err)
        uploaded = False
    return uploaded
