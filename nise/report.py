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
"""Module responsible for generating the cost and usage report."""
import csv
import os
from tempfile import NamedTemporaryFile

from faker import Faker

from nise.generators import (COLUMNS,
                             DataTransferGenerator,
                             EBSGenerator,
                             EC2Generator,
                             S3Generator)
from nise.manifest import generate_manifest
from nise.upload import upload_to_s3


def _write_csv(output_file, data, header=COLUMNS):
    """Output csv file data."""
    with output_file as file:
        writer = csv.DictWriter(file, fieldnames=header)
        writer.writeheader()
        for row in data:
            writer.writerow(row)


def _write_manifest(data):
    """Write manifest file to temp location.

    Args:
        data    (String): data to store
    Returns:
        (String): Path to temporary file
    """
    t_file = NamedTemporaryFile(mode='w', suffix='.json', delete=False)
    t_file.write(data)
    t_file.flush()
    return t_file.name


# pylint: disable=too-many-locals
def create_report(output_file, options):
    """Create a cost usage report file."""
    generators = [DataTransferGenerator, EBSGenerator, EC2Generator, S3Generator]
    data = []
    start_date = options.get('start_date')
    end_date = options.get('end_date')
    fake = Faker()
    payer_account = fake.ean(length=13)  # pylint: disable=no-member
    for generator in generators:
        gen = generator(start_date, end_date, payer_account)
        data += gen.generate_data()

    _write_csv(output_file, data)

    bucket_name = options.get('bucket_name')
    if bucket_name:
        report_name = options.get('report_name')
        manifest_values = {'account': payer_account}
        manifest_values.update(options)
        s3_cur_path, manifest_data = generate_manifest(fake, manifest_values)
        s3_manifest_path = os.path.dirname(s3_cur_path) + '/'
        s3_manifest_path = s3_manifest_path + report_name + '-Manifest.json'
        temp_manifest = _write_manifest(manifest_data)
        upload_to_s3(bucket_name,
                     s3_manifest_path,
                     temp_manifest)
        upload_to_s3(bucket_name,
                     s3_cur_path,
                     output_file.name)
        os.remove(temp_manifest)
