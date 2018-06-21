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
"""Defines the upload mechanism to AWS."""

import boto3
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
    except (ClientError, BotoConnectionError,
            boto3.exceptions.S3UploadFailedError) as upload_err:
        print(upload_err)
        uploaded = False
    return uploaded
