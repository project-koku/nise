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

from nise.report import (aws_create_report,
                         ocp_create_report)


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
    provider_group = parser.add_mutually_exclusive_group(required=True)
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
    provider_group.add_argument('--aws',
                                dest='aws',
                                action='store_true',
                                help='Create AWS cost and usage report data.')
    provider_group.add_argument('--ocp',
                                dest='ocp',
                                action='store_true',
                                help='Create OCP usage report data.')
    parser.add_argument('--aws-s3-bucket-name',
                        metavar='BUCKET_NAME',
                        dest='aws_bucket_name',
                        required=False,
                        help='AWS S3 bucket to place the data.')
    parser.add_argument('--aws-s3-report-name',
                        metavar='COST_REPORT_NAME',
                        dest='aws_report_name',
                        required=False,
                        help='Directory path to store data in the S3 bucket.')
    parser.add_argument('--aws-s3-report-prefix',
                        metavar='PREFIX_NAME',
                        dest='aws_prefix_name',
                        required=False,
                        help='Directory path to store data in the S3 bucket.')
    parser.add_argument('--aws-finalize',
                        metavar='FINALIZE_REPORT',
                        dest='aws_finalize_report',
                        choices=['copy', 'overwrite'],
                        required=False,
                        help="""Whether to generate finalized report data.
                            Can be either \'copy\' to produce a second finalized file locally
                            or \'overwrite\' to finalize the normal report files.
                            """)
    parser.add_argument('--ocp-cluster-id',
                        metavar='OCP_CLUSTER_ID',
                        dest='ocp_cluster_id',
                        required=False,
                        help='Cluster identifier for usage data.')

    return parser


def _get_aws_options(options):
    """Obtain all the aws options.

    Args:
        options (Dict): dictionary of arguments.
    Returns:
        aws_bucket_name (string): AWS bucket name
        aws_report_name (string): AWS report name
        aws_prefix_name (string): AWS report prefix
        aws_finalize_report (string): AWS finalize choice

    """
    aws_bucket_name = options.get('aws_bucket_name')
    aws_report_name = options.get('aws_report_name')
    aws_prefix_name = options.get('aws_prefix_name')
    aws_finalize_report = options.get('aws_finalize_report')
    return (aws_bucket_name, aws_report_name, aws_prefix_name, aws_finalize_report)


def _get_ocp_options(options):
    """Obtain all the ocp options.

    Args:
        options (Dict): dictionary of arguments.
    Returns:
        ocp_cluster_id (string): OCP cluster id

    """
    ocp_cluster_id = options.get('ocp_cluster_id')
    return (ocp_cluster_id,)


def _validate_aws_arguments(parser, options):
    """Validate aws argument combination.

    Args:
        parser (Object): ArgParser parser.
        options (Dict): dictionary of arguments.
    Raises:
        (ParserError): If combination is invalid.

    """
    aws_valid = False
    ocp_options = _get_ocp_options(options)
    for ocp_option in ocp_options:
        if ocp_option is not None:
            msg = 'OCP arguments cannot be supplied when generating AWS data.'
            parser.error(msg)

    aws_bucket_name, aws_report_name, _, _ = _get_aws_options(options)
    if aws_bucket_name and aws_report_name:
        aws_valid = True
    elif not aws_bucket_name and not aws_report_name:
        aws_valid = True
    if not aws_valid:
        msg = 'Both {} and {} must be supplied, if one is provided.'
        msg = msg.format('--aws-s3-bucket-name', '--aws-s3-report-name')
        parser.error(msg)
    return aws_valid


def _validate_ocp_arguments(parser, options):
    """Validate ocp argument combination.

    Args:
        parser (Object): ArgParser parser.
        options (Dict): dictionary of arguments.
    Raises:
        (ParserError): If combination is invalid.

    """
    ocp_valid = False
    aws_options = _get_aws_options(options)
    for aws_option in aws_options:
        if aws_option is not None:
            msg = 'AWS arguments cannot be supplied when generating OCP data.'
            parser.error(msg)

    ocp_cluster_id, = _get_ocp_options(options)
    if ocp_cluster_id is None:
        msg = '{} must be supplied.'
        msg = msg.format('--ocp-cluster-id')
        parser.error(msg)
    else:
        ocp_valid = True
    return ocp_valid


def _validate_provider_inputs(parser, options):
    """Validate provider inputs.

    Args:
        parser (Object): ArgParser parser.
        options (Dict): dictionary of arguments.
    Raises:
        (ParserError): If combination is invalid.

    """
    valid_inputs = False
    provider_type = None
    aws = options.get('aws', False)
    ocp = options.get('ocp', False)
    if aws:
        valid_inputs = _validate_aws_arguments(parser, options)
        provider_type = 'aws'
    elif ocp:
        valid_inputs = _validate_ocp_arguments(parser, options)
        provider_type = 'ocp'
    else:
        msg = 'Either {} or {} must be supplied to generate a report.'
        msg = msg.format('--aws', '--ocp')
        parser.error(msg)
    return (valid_inputs, provider_type)


def main():
    """Run data generation program."""
    parser = create_parser()
    args = parser.parse_args()
    options = vars(args)
    _, provider_type = _validate_provider_inputs(parser, options)
    if provider_type == 'aws':
        aws_create_report(options)
    elif provider_type == 'ocp':
        ocp_create_report(options)


if __name__ == '__main__':
    main()
