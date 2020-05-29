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
import logging
import os

from dateutil.parser import parse
from nise.yaml_generators.aws.generator import AWSGenerator
from nise.yaml_generators.ocp.generator import OCPGenerator

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(os.path.dirname(FILE_DIR), "nise/yaml_generators/static")

GENERATOR_MAP = {"AWS": AWSGenerator(), "OCP": OCPGenerator()}

LOG = logging.getLogger(__name__)


class DateRangeArgsError(Exception):
    """Date range args exception."""

    pass


def add_yaml_parser_args(yaml_parser):
    """
    Initialize the argument parser.

    Returns:
        ArgumentParser
    """
    yaml_parser.add_argument(
        "-o", "--output", dest="output_file_name", type=str, required=True, metavar="FILE", help="Output file path."
    )
    yaml_parser.add_argument(
        "-c", "--config", dest="config_file_name", type=str, required=False, metavar="CONF", help="Config file path."
    )
    yaml_parser.add_argument(
        "-t",
        "--template",
        dest="template_file_name",
        type=str,
        required=False,
        metavar="TMPL",
        help="Template file path.",
    )
    yaml_parser.add_argument(
        "-s",
        "--start-date",
        dest="start_date",
        type=str,
        required=False,
        metavar="YYYY-MM-DD",
        help="Start date (overrides template, default is first day of last month)",
    )
    yaml_parser.add_argument(
        "-e",
        "--end-date",
        dest="end_date",
        type=str,
        required=False,
        metavar="YYYY-MM-DD",
        help="End date (overrides template, default is last day of current month)",
    )
    yaml_parser.add_argument(
        "-n",
        "--num-nodes",
        dest="num_nodes",
        type=int,
        required=False,
        metavar="INT",
        help="Number of nodes to generate (overrides template, default is 1)",
    )
    yaml_parser.add_argument(
        "-r",
        "--random",
        dest="random",
        action="store_true",
        required=False,
        default=False,
        help="Randomize the number of nodes, namespaces, pods, volumes, volume-claims (default is False)",
    )
    yaml_parser.add_argument(
        "-p", "--provider", dest="provider", type=str, required=True, help="The provider type (AWS or OCP)"
    )

    return yaml_parser


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

    if args.num_nodes is not None and args.num_nodes < 1:
        args.num_nodes = None

    return args


def yaml_main(args):
    """YAML File generator main()."""
    args = handle_args(args)
    generator = GENERATOR_MAP.get(args.provider.upper())
    if not generator:
        LOG.warning("Provider import not found.")
        return

    config = generator.init_config(args)
    generator.process_template(args, config)
