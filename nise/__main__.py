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
import calendar
import datetime
import os

import yaml
from dateutil import parser as date_parser
from dateutil.relativedelta import relativedelta

from nise.report import (aws_create_report,
                         azure_create_report,
                         ocp_create_report)


def valid_date(date_string):
    """Create date from date string."""
    try:
        valid = datetime.datetime.strptime(date_string, '%Y-%m-%d')
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
                        required=False,
                        type=valid_date,
                        help='Date to start generating data (YYYY-MM-DD)')
    parser.add_argument('--end-date',
                        metavar='DATE',
                        dest='end_date',
                        required=False,
                        type=valid_date,
                        default=today(),
                        help='Date to end generating data (YYYY-MM-DD). Default is today.')
    provider_group.add_argument('--aws',
                                dest='aws',
                                action='store_true',
                                help='Create AWS cost and usage report data.')
    provider_group.add_argument('--azure',
                                dest='azure',
                                action='store_true',
                                help='Create Azure cost and usage report data.')
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
    parser.add_argument('--azure-storage-name',
                        metavar='AZURE_STORAGE_NAME',
                        dest='azure_storage_name',
                        required=False,
                        help='Azure storage account to place the data.')
    parser.add_argument('--azure-report-name',
                        metavar='AZURE_COST_REPORT_NAME',
                        dest='azure_report_name',
                        required=False,
                        help='Directory path to store data in the bucket.')
    parser.add_argument('--azure-storage-report-prefix',
                        metavar='AZURE_PREFIX_NAME',
                        dest='azure_prefix_name',
                        required=False,
                        help='Directory path to store data in the bucket.')
    parser.add_argument('--static-report-file',
                        dest='static_report_file',
                        required=False,
                        help='Generate static data based on yaml.')
    parser.add_argument('--ocp-cluster-id',
                        metavar='OCP_CLUSTER_ID',
                        dest='ocp_cluster_id',
                        required=False,
                        help='Cluster identifier for usage data.')
    parser.add_argument('--insights-upload',
                        metavar='UPLOAD_ENDPOINT',
                        dest='insights_upload',
                        required=False,
                        help='URL for Insights Upload Service.')

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


def _get_azure_options(options):
    """Obtain all the azure options.

    Args:
        options (Dict): dictionary of arguments.
    Returns:
        azure_storage_name (string): Azure storage account name
        azure_report_name (string): Azure report name
        azure_prefix_name (string): Azure report prefix
        azure_finalize_report (string): Azure finalize choice

    """
    azure_storage_name = options.get('azure_storage_name')
    azure_report_name = options.get('azure_report_name')
    azure_prefix_name = options.get('azure_prefix_name')
    # azure_finalize_report = options.get('azure_finalize_report')
    return (azure_storage_name, azure_report_name, azure_prefix_name)


def _get_ocp_options(options):
    """Obtain all the ocp options.

    Args:
        options (Dict): dictionary of arguments.
    Returns:
        ocp_cluster_id (string): OCP cluster id

    """
    ocp_cluster_id = options.get('ocp_cluster_id')
    insights_upload = options.get('insights_upload')
    return (ocp_cluster_id, insights_upload)


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
    azure_options = _get_azure_options(options)
    for ocp_option in ocp_options:
        if ocp_option is not None:
            msg = 'OCP arguments cannot be supplied when generating AWS data.'
            parser.error(msg)
    for azure_option in azure_options:
        if azure_option is not None:
            msg = 'Azure arguments cannot be supplied when generating AWS data.'
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


def _validate_azure_arguments(parser, options):
    """Validate azure argument combination.

    Args:
        parser (Object): ArgParser parser.
        options (Dict): dictionary of arguments.
    Raises:
        (ParserError): If combination is invalid.

    """
    azure_valid = False
    ocp_options = _get_ocp_options(options)
    aws_options = _get_aws_options(options)
    for ocp_option in ocp_options:
        if ocp_option is not None:
            msg = 'OCP arguments cannot be supplied when generating Azure data.'
            parser.error(msg)
    for aws_option in aws_options:
        if aws_option is not None:
            msg = 'AWS arguments cannot be supplied when generating Azure data.'
            parser.error(msg)

    azure_storage_name, azure_report_name, _ = _get_azure_options(options)
    if azure_storage_name and azure_report_name:
        azure_valid = True
    elif not azure_storage_name and not azure_report_name:
        azure_valid = True
    if not azure_valid:
        msg = 'Both {} and {} must be supplied, if one is provided.'
        msg = msg.format('--azure-storage-name', '--azure-report-name')
        parser.error(msg)
    return azure_valid


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
    azure_options = _get_azure_options(options)
    for aws_option in aws_options:
        if aws_option is not None:
            msg = 'AWS arguments cannot be supplied when generating OCP data.'
            parser.error(msg)
    for azure_option in azure_options:
        if azure_option is not None:
            msg = 'Azure arguments cannot be supplied when generating AWS data.'
            parser.error(msg)

    ocp_cluster_id, insights_upload = _get_ocp_options(options)
    if ocp_cluster_id is None:
        msg = '{} must be supplied.'
        msg = msg.format('--ocp-cluster-id')
        parser.error(msg)
    elif insights_upload is not None and not os.path.isdir(insights_upload):
        insights_user = os.environ.get('INSIGHTS_USER')
        insights_password = os.environ.get('INSIGHTS_PASSWORD')
        insights_account_id = os.environ.get('INSIGHTS_ACCOUNT_ID')
        insights_org_id = os.environ.get('INSIGHTS_ORG_ID')
        if (insights_account_id is None or insights_org_id is None) and \
                (insights_user is None or insights_password is None):
            msg = 'The environment must have \nINSIGHTS_USER and ' \
                'INSIGHTS_PASSWORD or\nINSIGHTS_ACCOUNT_ID and INSIGHTS_ORG_ID' \
                'defined when {} {} is supplied.'
            msg = msg.format('--insights-upload', insights_upload)
            parser.error(msg)
        # Either set of acceptable credentials are acceptable
        ocp_valid = True
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
    azure = options.get('azure', False)
    ocp = options.get('ocp', False)
    if aws:
        valid_inputs = _validate_aws_arguments(parser, options)
        provider_type = 'aws'
    elif azure:
        valid_inputs = _validate_azure_arguments(parser, options)
        provider_type = 'azure'
    elif ocp:
        valid_inputs = _validate_ocp_arguments(parser, options)
        provider_type = 'ocp'
    else:
        msg = 'One of {}, {}, or {} must be supplied to generate a report.'
        msg = msg.format('--aws', '--azure', '--ocp')
        parser.error(msg)
    return (valid_inputs, provider_type)


def _load_yaml_file(filename):
    """Local data from yaml file."""
    yamlfile = None
    if filename:
        try:
            with open(filename, 'r+') as yaml_file:
                yamlfile = yaml.load(yaml_file, Loader=yaml.FullLoader)
        except TypeError:
            yamlfile = yaml.load(filename)
    return yamlfile


def _load_static_report_data(options):
    """Validate/load and set start_date if static file is provided."""
    if options.get('static_report_file'):
        start_dates = []
        end_dates = []
        static_report_data = _load_yaml_file(options.get('static_report_file'))
        for generator_dict in static_report_data.get('generators'):
            for _, attributes in generator_dict.items():
                if attributes.get('start_date'):
                    generated_start_date = calculate_start_date(attributes.get('start_date'))
                    start_dates.append(generated_start_date)

                if attributes.get('end_date'):
                    generated_end_date = calculate_end_date(
                        generated_start_date,
                        attributes.get('end_date')
                    )
                else:
                    if options.get('azure'):
                        generated_end_date = today() + datetime.timedelta(hours=24)
                    else:
                        generated_end_date = today()
                end_dates.append(generated_end_date)

                attributes['start_date'] = str(generated_start_date)
                attributes['end_date'] = str(generated_end_date)

            options['start_date'] = min(start_dates)
            latest_date = max(end_dates)
            last_day_of_month = calendar.monthrange(year=latest_date.year,
                                                    month=latest_date.month)[1]
            options['end_date'] = latest_date.replace(day=last_day_of_month, hour=0, minute=0)
            options['static_report_data'] = static_report_data


def calculate_start_date(start_date):
    """Return a datetime for the start date."""
    if start_date == 'last_month':
        generated_start_date = today().replace(day=1, hour=0, minute=0, second=0) + \
            relativedelta(months=-1)
    elif start_date == 'today':
        generated_start_date = today().replace(hour=0, minute=0, second=0)
    elif start_date and isinstance(start_date, datetime.date):
        generated_start_date = datetime.datetime.fromordinal(start_date.toordinal())
    elif start_date:
        generated_start_date = date_parser.parse(start_date)
    else:
        generated_start_date = today().replace(day=1, hour=0, minute=0, second=0)
    return generated_start_date


def calculate_end_date(start_date, end_date):
    """Return a datetime for the end date."""
    try:
        if end_date and isinstance(end_date, datetime.date):
            generated_end_date = datetime.datetime.fromordinal(end_date.toordinal())
        else:
            generated_end_date = date_parser.parse(end_date)
    except TypeError:
        offset = end_date
        offset_date = start_date + relativedelta(days=offset)
        if offset_date.month > start_date.month:
            generated_end_date = offset_date
        else:
            generated_end_date = min(start_date + relativedelta(days=offset),
                                     today())
    return generated_end_date


def main():
    """Run data generation program."""
    parser = create_parser()
    args = parser.parse_args()
    options = vars(args)
    _load_static_report_data(options)
    _, provider_type = _validate_provider_inputs(parser, options)
    if not options.get('start_date'):
        parser.error('the following arguments are required: --start-date')
    if provider_type == 'aws':
        aws_create_report(options)
    elif provider_type == 'azure':
        azure_create_report(options)
    elif provider_type == 'ocp':
        ocp_create_report(options)


if __name__ == '__main__':
    main()
