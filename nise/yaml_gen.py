#
# Copyright 2020 Red Hat, Inc.
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
"""YAML File Generator."""
import argparse
import logging
import os

from dateutil.parser import parse
from nise.yaml_generators.aws.generator import AWSGenerator
from nise.yaml_generators.azure.generator import AzureGenerator
from nise.yaml_generators.ocp.generator import OCPGenerator
from nise.yaml_generators.ocp_on_x.generator import OCPonXGenerator

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(os.path.dirname(FILE_DIR), "nise/yaml_generators/static")

GENERATOR_MAP = {
    "AWS": AWSGenerator(),
    "OCP": OCPGenerator(),
    "AZURE": AzureGenerator(),
    "OCP-ON-X": OCPonXGenerator(),
}

LOG = logging.getLogger(__name__)


class DateRangeArgsError(Exception):
    """Date range args exception."""

    pass


def add_aws_args(parser):
    """Add AWS specific parser args."""
    pass


def add_azure_args(parser):
    """Add Azure specific parser args."""
    pass


def add_gcp_args(parser):
    """Add GCP specific parser args."""
    pass


def add_ocp_args(parser):
    """Add OCP specific parser args."""
    parser.add_argument(
        "-n",
        "--num-nodes",
        dest="num_nodes",
        type=int,
        required=False,
        metavar="INT",
        help="Number of nodes to generate (overrides template, default is 1)",
    )


def add_ocp_on_x_args(parser):
    """Add OCP-on-X specific parser args."""
    add_ocp_args(parser)


def add_yaml_parser_args(yaml_parser):
    """
    Initialize the argument parser.

    Returns:
        ArgumentParser
    """
    parent_parser = argparse.ArgumentParser()
    parent_parser.add_argument(
        "-o", "--output", dest="output_file_name", type=str, required=True, metavar="FILE", help="Output file path."
    )
    parent_parser.add_argument(
        "-c", "--config", dest="config_file_name", type=str, required=False, metavar="CONF", help="Config file path."
    )
    parent_parser.add_argument(
        "-t",
        "--template",
        dest="template_file_name",
        type=str,
        required=False,
        metavar="TMPL",
        help="Template file path.",
    )
    parent_parser.add_argument(
        "-s",
        "--start-date",
        dest="start_date",
        type=str,
        required=False,
        metavar="YYYY-MM-DD",
        help="Start date (overrides template, default is first day of last month)",
    )
    parent_parser.add_argument(
        "-e",
        "--end-date",
        dest="end_date",
        type=str,
        required=False,
        metavar="YYYY-MM-DD",
        help="End date (overrides template, default is last day of current month)",
    )
    parent_parser.add_argument(
        "-r",
        "--random",
        dest="random",
        action="store_true",
        required=False,
        default=False,
        help="Randomize the number of nodes, namespaces, pods, volumes, volume-claims (default is False)",
    )
    yaml_subparser = yaml_parser.add_subparsers(dest="provider")
    aws_parser = yaml_subparser.add_parser(
        "aws", parents=[parent_parser], add_help=False, description="The AWS parser", help="create the AWS yamls"
    )
    azure_parser = yaml_subparser.add_parser(
        "azure", parents=[parent_parser], add_help=False, description="The Azure parser", help="create the Azure yamls"
    )
    ocp_parser = yaml_subparser.add_parser(
        "ocp", parents=[parent_parser], add_help=False, description="The OCP parser", help="create the OCP yamls"
    )
    ocp_on_x_parser = yaml_subparser.add_parser(
        "ocp-on-x",
        parents=[parent_parser],
        add_help=False,
        description="The OCP-on-X parser",
        help="create the OCP-on-X yamls",
    )

    add_aws_args(aws_parser)
    add_azure_args(azure_parser)
    add_ocp_args(ocp_parser)
    add_ocp_on_x_args(ocp_on_x_parser)

    return yaml_parser


def handle_ocp_args(args):
    """Parse and validate OCP specific args."""
    if args.num_nodes is not None and args.num_nodes < 1:
        args.num_nodes = None
    return args


def handle_args(args):
    """
    Parse and validate the arguments.

    Returns:
        Namespace
    """
    if args.config_file_name == "default":
        args.config_file_name = os.path.join(STATIC_DIR, f"{args.provider.lower()}_generator_config.yml")

    if args.config_file_name and not os.path.exists(args.config_file_name):
        raise FileNotFoundError(f'Cannot find file "{args.config_file_name}"')

    if args.template_file_name and not os.path.exists(args.template_file_name):
        raise FileNotFoundError(f'Cannot find file "{args.template_file_name}"')

    if not args.template_file_name:
        args.template_file_name = os.path.join(STATIC_DIR, f"{args.provider.lower()}_static_data.yml.j2")

    if int(bool(args.start_date)) + int(bool(args.end_date)) == 1:
        raise DateRangeArgsError("The full date range must be supplied or omitted.")

    if args.start_date:
        args.start_date = parse(args.start_date).date()
    if args.end_date:
        args.end_date = parse(args.end_date).date()

    if args.provider == "ocp":
        args = handle_ocp_args(args)

    return args


def yaml_main(args):
    """YAML File generator main()."""
    args = handle_args(args)
    generator = GENERATOR_MAP.get(args.provider.upper())
    if not generator:
        raise NotImplementedError(f"Invalid provider type: {args.provider.upper()} not implemented")

    config = generator.init_config(args)
    generator.process_template(args, config)
