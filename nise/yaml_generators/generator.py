#! /usr/bin/env python3
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
"""Utility to generate large yaml files."""
import os
import sys
from abc import ABC

import yaml
from dateutil.parser import parse
from jinja2 import Environment
from jinja2 import FileSystemLoader


class Generator(ABC):
    """YAML File Generator base class."""

    def default_config(self, *args, **kwargs):
        """Defaulted config abstract method."""
        raise NotImplementedError

    def validate_config(self, *args, **kwargs):
        """Validate config abstract method."""
        raise NotImplementedError

    def build_data(self, *args, **kwargs):
        """Build data abstract method."""
        raise NotImplementedError

    def init_config(self, args):
        """
        Initialize the config object for template processing.

        Params:
            args : Namespace - Command line arguments
        Returns:
            dicta - The initialized config object
        """
        config = self.default_config()

        # override default with settings
        if args.config_file_name:
            with open(args.config_file_name, "rt") as settings_file:
                config_settings = yaml.safe_load(settings_file)
            config.update(config_settings)

        # override config with args
        if args.start_date:
            config.start_date = args.start_date
        if isinstance(config.start_date, str):
            config.start_date = parse(config.start_date)
        if args.end_date:
            config.end_date = args.end_date
        if isinstance(config.end_date, str):
            config.end_date = parse(config.end_date)

        return config

    def process_template(self, args, config):
        """
        Process the jinja2 template using supplied parameter data.

        Produces an output file (if specified) or writes data to stdout.

        Parameters:
            args : Namespace - Command line arguments
            config : dicta - Template data generation config data
        Returns:
            None
        """
        self.validate_config(config)
        data = self.build_data(config, args.random)

        template_file_name = os.path.abspath(args.template_file_name)
        template_loader = FileSystemLoader(os.path.dirname(template_file_name))
        env = Environment(loader=template_loader)
        template = env.get_template(os.path.basename(template_file_name))

        output = template.render(generator=data)

        if args.output_file_name == sys.stdout:
            sys.stdout.write(output)
            sys.stdout.flush()
        else:
            with open(args.output_file_name, "wt") as outf:
                outf.write(output)
                outf.flush()
