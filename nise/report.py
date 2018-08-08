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
import calendar
import csv
import gzip
import os
from datetime import datetime
from tempfile import NamedTemporaryFile

from dateutil.relativedelta import relativedelta
from faker import Faker

from nise.copy import copy_to_local_dir
from nise.generators import (COLUMNS,
                             DataTransferGenerator,
                             EBSGenerator,
                             EC2Generator,
                             S3Generator)
from nise.manifest import generate_manifest
from nise.upload import upload_to_s3


def _write_csv(output_file, data, header=COLUMNS):
    """Output csv file data."""
    with open(output_file, 'w') as file:
        writer = csv.DictWriter(file, fieldnames=header)
        writer.writeheader()
        for row in data:
            writer.writerow(row)


def _gzip_report(report_path):
    """Compress the report."""
    t_file = NamedTemporaryFile(mode='wb', suffix='.csv.gz', delete=False)
    with open(report_path, 'rb') as f_in, gzip.open(t_file.name, 'wb') as f_out:
        f_out.write(f_in.read())
    return t_file.name


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


def route_file(bucket_name, bucket_file_path, local_path):
    """Route file to either S3 bucket or local filesystem."""
    if os.path.isdir(bucket_name):
        copy_to_local_dir(bucket_name,
                          bucket_file_path,
                          local_path)
    else:
        upload_to_s3(bucket_name,
                     bucket_file_path,
                     local_path)


def _create_month_list(start_date, end_date):
    """Create a list of months given the date range args."""
    months = []
    current = start_date

    if start_date.month == end_date.month:
        # No month range
        month = {}
        month['name'] = calendar.month_name[start_date.month]
        month['start'] = start_date
        month['end'] = end_date
        months.append(month)
    else:
        while current <= end_date:
            month = {}
            month['name'] = calendar.month_name[current.month]
            if current.month == start_date.month:
                # First month
                month['start'] = start_date
                month['end'] = datetime(year=current.year,
                                        month=current.month,
                                        day=calendar.monthrange(year=current.year,
                                                                month=current.month)[1])
            else:
                month['start'] = datetime(year=current.year, month=current.month, day=1)
                month['end'] = datetime(year=current.year,
                                        month=current.month,
                                        day=calendar.monthrange(year=current.year,
                                                                month=current.month)[1])
            months.append(month)
            current += relativedelta(months=+1)

    return months


# pylint: disable=too-many-locals
def create_report(output_file, options):
    """Create a cost usage report file."""
    generators = [DataTransferGenerator, EBSGenerator, EC2Generator, S3Generator]
    data = []
    start_date = options.get('start_date')
    end_date = options.get('end_date')
    months = _create_month_list(start_date, end_date)
    fake = Faker()
    payer_account = fake.ean(length=13)  # pylint: disable=no-member
    usage_accounts = (payer_account,
                      fake.ean(length=13),  # pylint: disable=no-member
                      fake.ean(length=13),  # pylint: disable=no-member
                      fake.ean(length=13),  # pylint: disable=no-member
                      fake.ean(length=13))  # pylint: disable=no-member
    for month in months:
        for generator in generators:
            gen = generator(month.get('start'), month.get('end'), payer_account, usage_accounts)
            data += gen.generate_data()

        file_path = os.path.dirname(output_file.name)
        if not file_path:
            file_path = os.getcwd()
        file_name = os.path.basename(output_file.name)
        month_output_file_name = '{}-{}-{}'.format(month.get('name'),
                                                   month.get('start').year,
                                                   file_name)
        month_output_file = '{}/{}'.format(file_path, month_output_file_name)
        _write_csv(month_output_file, data)

        bucket_name = options.get('bucket_name')
        if bucket_name:
            report_name = options.get('report_name')
            manifest_values = {'account': payer_account}
            manifest_values.update(options)
            manifest_values['start_date'] = month.get('start')
            manifest_values['end_date'] = month.get('end')
            s3_cur_path, manifest_data = generate_manifest(fake, manifest_values)
            s3_assembly_path = os.path.dirname(s3_cur_path)
            s3_month_path = os.path.dirname(s3_assembly_path)
            s3_month_manifest_path = s3_month_path + '/' + report_name + '-Manifest.json'
            s3_assembly_manifest_path = s3_assembly_path + '/' + report_name + '-Manifest.json'
            temp_manifest = _write_manifest(manifest_data)
            temp_cur_zip = _gzip_report(month_output_file)
            route_file(bucket_name,
                       s3_month_manifest_path,
                       temp_manifest)
            route_file(bucket_name,
                       s3_assembly_manifest_path,
                       temp_manifest)
            route_file(bucket_name,
                       s3_cur_path,
                       temp_cur_zip)
            os.remove(temp_manifest)
            os.remove(temp_cur_zip)
