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
"""Defines the upload mechanism to AWS and Azure."""
import os

import boto3
from azure.storage.blob import BlockBlobService
from botocore.exceptions import ClientError
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
        s3_client = boto3.resource('s3')
        s3_client.Bucket(bucket_name).upload_file(local_path,
                                                  bucket_file_path)
        msg = 'Uploaded {} to s3 bucket {}.'.format(
            bucket_file_path, bucket_name)
        print(msg)
    except (ClientError, BotoConnectionError,
            boto3.exceptions.S3UploadFailedError) as upload_err:
        print(upload_err)
        uploaded = False
    return uploaded


def upload_to_storage(storage_file_name, local_path, storage_file_path):
    """Upload data to a storage account.

    Args:
        storage_file_name (String): The container to upload file to
        local_path  (String): The full local file system path of the file
        storage_file_path (String): The file path to upload to within container
    Returns:
        (Boolean): True if file was uploaded

    """
    uploaded = True
    try:
        account_key = str(os.environ.get('AZURE_ACCOUNT_KEY'))
        storage_account = str(os.environ.get('AZURE_STORAGE_ACCOUNT'))
        # Create the BlockBlockService that is used to call the
        # Blob service for the storage account.
        block_blob_service = BlockBlobService(
            account_name=storage_account, account_key=account_key)

        # Upload the created file, use local_file_name for the blob name.
        block_blob_service.create_blob_from_path(
            storage_file_name, storage_file_path, local_path)
    # pylint: disable=broad-except
    except Exception as error:
        print(error)
        uploaded = False
    return uploaded
