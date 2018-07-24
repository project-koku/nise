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

import os
import shutil


def copy_to_local_dir(bucket_name, bucket_file_path, local_path):
    """Upload data to an S3 bucket.

    Args:
        bucket_name (String): Local file path representing the bucket
        bucket_file_path (String): The path to store the file to
        local_path  (String): The local file system path of the file
    Returns:
        (Boolean): True if file was uploaded
    """
    if not os.path.isdir(bucket_name):
        print('Path does not exist for the bucket: {}'.format(bucket_name))
        return False

    full_bucket_path = '{}{}'.format(bucket_name, bucket_file_path)
    os.makedirs(os.path.dirname(full_bucket_path), exist_ok=True)
    shutil.copy2(local_path, full_bucket_path)
    msg = 'Copied {} to s3 bucket {}.'.format(bucket_file_path, bucket_name)
    print(msg)
    return True
