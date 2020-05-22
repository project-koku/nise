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
import argparse
from datetime import date
from unittest import TestCase

from nise import yaml_gen


class YamlGeneratorTestCase(TestCase):
    """
    Base TestCase class, sets up a CLI parser
    """

    def test_init_args(self):
        """
        Test creation of the argument parser
        """
        p = argparse.ArgumentParser()
        result = yaml_gen.add_yaml_parser_args(p)
        self.assertTrue(isinstance(result, argparse.ArgumentParser))

    def test_handle_missing_start_date_arg(self):
        """
        Test the argument handler end range only
        """
        args = argparse.Namespace()
        args.end_date = "9999-12-31"
        args.template_file_name = __file__
        args.config_file_name = args.start_date = args.num_nodes = None
        args.random = False
        with self.assertRaises(yaml_gen.DateRangeArgsError):
            yaml_gen.handle_args(args)

    def test_handle_missing_end_date_arg(self):
        """
        Test the argument handler start range only
        """
        args = argparse.Namespace()
        args.start_date = "9999-12-31"
        args.template_file_name = __file__
        args.config_file_name = args.end_date = args.num_nodes = None
        args.random = False
        with self.assertRaises(yaml_gen.DateRangeArgsError):
            yaml_gen.handle_args(args)

    def test_handle_args_date_range(self):
        """
        Test the argument handler start and end range
        """
        args = argparse.Namespace()
        args.start_date = "9999-12-31"
        args.end_date = "9999-12-31"
        args.template_file_name = __file__
        args.config_file_name = args.num_nodes = None
        args.random = False
        yaml_gen.handle_args(args)
        self.assertTrue(isinstance(args.start_date, date))
        self.assertTrue(isinstance(args.end_date, date))

    def test_unfindable_args_template_file(self):
        """
        Test unfindable template file
        """
        args = argparse.Namespace()
        args.template_file_name = "\b"
        args.start_date = args.end_date = args.config_file_name = args.num_nodes = None
        args.random = False
        with self.assertRaises(FileNotFoundError):
            yaml_gen.handle_args(args)

    def test_unfindable_args_config_file(self):
        """
        Test unfindable config file
        """
        args = argparse.Namespace()
        args.config_file_name = "\b"
        args.template_file_name = __file__
        args.start_date = args.end_date = args.num_nodes = None
        with self.assertRaises(FileNotFoundError):
            yaml_gen.handle_args(args)

    def test_zero_num_nodes_arg(self):
        """
        Test zero num_nodes arg
        """
        args = argparse.Namespace()

        args.template_file_name = __file__
        args.start_date = args.end_date = args.config_file_name = None
        args.num_nodes = 0
        args = yaml_gen.handle_args(args)
        self.assertTrue(args.num_nodes is None)

    def test_negative_num_nodes_arg(self):
        """
        Test negative num_nodes arg
        """
        args = argparse.Namespace()

        args.template_file_name = __file__
        args.num_nodes = -1
        args.start_date = args.end_date = args.config_file_name = None
        args = yaml_gen.handle_args(args)
        self.assertTrue(args.num_nodes is None)

    def test_positive_num_nodes_arg(self):
        """
        Test positive num_nodes arg
        """
        args = argparse.Namespace()

        args.template_file_name = __file__
        args.num_nodes = 10
        args.start_date = args.end_date = args.config_file_name = None
        args = yaml_gen.handle_args(args)
        self.assertEqual(args.num_nodes, 10)
