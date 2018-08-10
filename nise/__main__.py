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
"""Cost and Usage Generator CLI."""

import argparse
import datetime

from nise.report import create_report


def valid_date(date_string):
    """Create date from date string."""
    try:
        valid = datetime.datetime.strptime(date_string, '%m-%d-%Y')
    except ValueError:
        msg = '{} is an unsupported date format.'.format(date_string)
        raise argparse.ArgumentTypeError(msg)
    return valid


def today():
    """Create the date of today."""
    return datetime.datetime.now().replace(microsecond=0, second=0, minute=0)


def create_parser():
    """Create the parser for incoming data."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--start-date',
                        metavar='DATE',
                        dest='start_date',
                        required=True,
                        type=valid_date,
                        help='Date to start generating data (MM-DD-YYYY)')
    parser.add_argument('--end-date',
                        metavar='DATE',
                        dest='end_date',
                        required=False,
                        type=valid_date,
                        default=today(),
                        help='Date to end generating data (MM-DD-YYYY). Default is today.')
    parser.add_argument('--s3-bucket-name',
                        metavar='BUCKET_NAME',
                        dest='bucket_name',
                        required=False,
                        help='AWS S3 bucket to place the data.')
    parser.add_argument('--s3-report-name',
                        metavar='COST_REPORT_NAME',
                        dest='report_name',
                        required=False,
                        help='Directory path to store data in the S3 bucket.')
    parser.add_argument('--s3-report-prefix',
                        metavar='PREFIX_NAME',
                        dest='prefix_name',
                        required=False,
                        help='Directory path to store data in the S3 bucket.')

    return parser


def _check_s3_arguments(parser, options):
    """Validate s3 argument combination.

    Args:
        parser (Object): ArgParser parser.
        options (Dict): dictionary of arguments.
    Raises:
        (ParserError): If combination is invalid.

    """
    bucket_name = options.get('bucket_name')
    report_name = options.get('report_name')
    s3_valid = False
    if bucket_name and report_name:
        s3_valid = True
    elif not bucket_name and not report_name:
        s3_valid = True
    if not s3_valid:
        msg = 'Both {} and {} must be supplied, if one is provided.'
        msg = msg.format('--s3-bucket-name', '--s3-report-name')
        parser.error(msg)
    return s3_valid


def main():
    """Run data generation program."""
    parser = create_parser()
    args = parser.parse_args()
    options = vars(args)
    _check_s3_arguments(parser, options)
    create_report(options)


if __name__ == '__main__':
    main()
