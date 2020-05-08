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
"""Defines the upload mechanism to local directories for simulation."""
import logging
import os
import shutil

LOG = logging.getLogger(__name__)


def copy_to_local_dir(local_dir_home, local_path, local_file_path=None):
    """Upload data to an local directory.

    Args:
        local_dir_home (String): Local file path representing the bucket
        local_path  (String): The local file system path of the file
        local_file_path (String): The path to store the file to
    Returns:
        (Boolean): True if file was uploaded

    """
    if not os.path.isdir(local_dir_home):
        LOG.info(f"Path does not exist for the local directory: {local_dir_home}")
        return False
    full_bucket_path = local_dir_home
    outpath = local_path
    if local_file_path:
        full_bucket_path = f"{local_dir_home}/{local_file_path}"
        outpath = local_file_path
    os.makedirs(os.path.dirname(full_bucket_path), exist_ok=True)
    shutil.copyfile(local_path, full_bucket_path)
    msg = f"Copied {outpath} to local directory {local_dir_home}."
    LOG.info(msg)
    return True
