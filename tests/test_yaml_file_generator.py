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
import os
from datetime import datetime, date
from importlib.machinery import SourceFileLoader
from unittest import TestCase
from unittest.mock import patch
import shutil


FILE_DIR = os.path.abspath(__file__)
UTILITY_DIR = os.path.join(os.path.sep, *FILE_DIR.split(os.path.sep)[:-2], 'utility')

CACHE_PATH = os.path.join(UTILITY_DIR, '__pycache__')
if os.path.exists(CACHE_PATH):
    shutil.rmtree(CACHE_PATH)

yg = SourceFileLoader('yaml_generator', os.path.join(UTILITY_DIR, 'generate_static_ocp_settings.py')).load_module()


class YamlGeneratorTestCase(TestCase):
    """
    Base TestCase class, sets up a CLI parser
    """
    def test_default_config(self):
        """Test default configuration."""
        dc = yg.default_config()
        self.assertTrue(isinstance(dc, yg.dicta))
        self.assertTrue(yg.validate_config(dc))


    def test_config_validator(self):
        """Test config validation """
        dc = yg.default_config()
        self.assertTrue(yg.validate_config(dc))
        with self.assertRaises(TypeError):
            dc.start_date = ''
            self.assertFalse(yg.validate_config(dc))


    def test_dicta(self):
        """
        Test dicta class
        """
        td = yg.dicta()
        self.assertEqual(len(td), 0)

        td.test = 1
        self.assertEqual(len(td), 1)
        self.assertEqual(td.test, td['test'])
        
        td.test = 2
        self.assertEqual(td.test, 2)
        
        td2 = td.copy()
        self.assertTrue(isinstance(td2, yg.dicta))
        self.assertEqual(td2, td)

        with self.assertRaises(KeyError):
            td.x
        
        del td.test
        self.assertEqual(len(td), 0)


    def test_word_generator(self):
        """
        Test the raw word generator
        """
        dc = yg.default_config()
        txt = yg.generate_words(dc)
        self.assertEqual(len(txt.split('-')), dc.name_wordiness)


    def test_number_str_generator(self):
        """
        Test the raw number string generator
        """
        dc = yg.default_config()
        txt = yg.generate_number_str(dc)
        self.assertTrue(txt.isdigit())
        self.assertEqual(len(txt), dc.max_resource_id_digits)


    def test_generate_name(self):
        """
        Test the name generator
        """
        dc = yg.default_config()
        name = yg.generate_name(dc)
        self.assertEqual(len(name.split('-')), dc.name_wordiness)
        self.assertFalse(name.isdigit())
        prefix = '___'
        suffix = '^^^'
        name = yg.generate_name(dc, prefix=prefix)
        self.assertTrue(name.startswith(prefix + '-'))
        self.assertTrue(len(name) - len(prefix + '-') > 0)
        name = yg.generate_name(dc, prefix=prefix, suffix=suffix)
        self.assertTrue(name.startswith(prefix + '-'))
        self.assertTrue(name.endswith('-' + suffix))
        self.assertTrue(len(name.replace(prefix + '-', '').replace('-' + suffix, '')) > 0)
        name = yg.generate_name(dc, prefix=prefix, suffix=suffix, dynamic=False)
        self.assertTrue(name.startswith(prefix + '-'))
        self.assertTrue(name.endswith('-' + suffix))
        self.assertTrue('--' not in name)
        self.assertEqual(len(name.replace(prefix + '-', '').replace('-' + suffix, '')), 0)


    def test_generate_resource_id(self):
        """ Test resource id generation """
        dc = yg.default_config()
        res_id = yg.generate_resource_id(dc)
        self.assertEqual(len(res_id), dc.max_resource_id_length)
        self.assertTrue(res_id.isdigit())


    def test_generate_labels(self):
        """
        Test label string generator
        """
        label_str = yg.generate_labels(0)
        self.assertEqual(len(label_str), 0)
        label_str = yg.generate_labels(2)
        labels = label_str.split('|')
        self.assertEqual(len(labels), 2)
        labels = [len(l.split(':')) == 2 for l in labels]
        self.assertTrue(all(labels))


    def test_build_data(self):
        """
        Test create data static and random
        """
        def check_exact(val, config_val):
            return val == config_val
        
        def check_range(val, config_val):
            return 1 <= val <= config_val
        
        def validate_data(config, _random, check_func):
            node_keys = sorted(['name', 'cpu_cores', 'memory_gig', 'resource_id', 'namespaces'])
            namespace_keys = sorted(['name', 'pods', 'volumes'])
            pod_keys = sorted(['name', 'cpu_request', 'mem_request_gig', 'cpu_limit', 'mem_limit_gig', 'pod_seconds', 'labels'])
            volume_keys = sorted(['name', 'storage_class', 'volume_request_gig', 'labels', 'volume_claims'])
            volume_claim_keys = sorted(['name', 'pod_name', 'labels' 'capacity_gig'])
            
            print(config, file=sys.stderr)

            data = yg.build_data(config, _random)
            self.assertTrue(isinstance(data, yg.dicta))

            self.assertTrue(isinstance(data.start_date, str) and isinstance(data.end_date, str))
            self.assertTrue(check_func(len(data.nodes), config.num_nodes))

            for node in data.nodes:
                self.assertEqual(sorted(node.keys()), node_keys)
                self.assertTrue(1 <= node.cpu_cores <= config.max_node_cpu_cores)
                self.assertTrue(1 <= node.memory_gig <= config.max_node_memory_gig)
                self.assertTrue(node.resource_id is not None and node.name is not None and node.name != '')
                self.assertEqual(len(node.namespaces), config.max_node_namespaces)

                for namespace in node.namespaces:
                    self.assertEqual(sorted(namespace.keys()), namespace_keys)
                    self.assertTrue(namespace.name is not None and namespace.name != '')
                    self.assertTrue(check_func(len(namespace.pods), config.max_node_namespace_pods))
                    self.assertTrue(check_func(len(namespace.volumes), config.max_node_namespace_volumes))
                    pod_names = [p.name for p in namespace.pods]
                    
                    for pod in namespace.pods:
                        self.assertEqual(sorted(pod.keys()), pod_keys)
                        self.assertTrue(1 <= pod.cpu_request <= node.cpu_cores)
                        self.assertTrue(1 <= pod.mem_request_gig <= node.memory_gig)
                        self.assertTrue(1 <= pod.cpu_limit <= node.cpu_cores)
                        self.assertTrue(1 <= pod.mem_limit_gig <= node.memory_gig)
                        self.assertTrue(config.min_node_namespace_pod_seconds <= pod.pod_seconds <= config.max_node_namespace_pod_seconds)
                        self.assertEqual(len(pod.labels.split('|')), config.max_node_namespace_pod_labels)
                        self.assertTrue(pod.name is not None and pod.name != '')
                    
                    for volume in namespace.volumes:
                        self.assertEqual(sorted(volume.keys()), volume_keys)
                        self.assertTrue(volume.storage_class in config.storage_classes)
                        self.assertTrue(1 <= volume.volume_request_gig <= config.max_node_namespace_volume_request_gig)
                        self.assertEqual(len(volume.labels.split('|')), config.max_node_namespace_volume_labels)
                        self.assertTrue(volume.name is not None and volume.name != '')
                        self.assertTrue(check_func(len(volume.volume_claims), config.max_node_namespace_volume_volume_claims))

                        for volume_claim in volume.volume_claims:
                            self.assertEqual(volume_claim.keys(), volume_claim_keys)
                            self.assertEqual(len(volume_claim.labels.split('|')), config.max_node_namespace_volume_volume_claim_labels)
                            self.assertTrue(volume_claim.name is not None and volume_claim.name != '')
                            self.assertTrue(volume_claim.pod_name in pod_names)
                            self.assertTrue(1 <= volume_claim.capacity_gig <= config.max_node_namespace_volume_volume_claim_capacity_gig)

        dc = yg.default_config()
        dc.num_nodes = 2
        dc.num_node_namespaces = 2
        dc.num_node_namespace_pods = 2
        dc.num_node_namespace_volumes = 2

        validate_data(dc, False, check_exact)
        validate_data(dc, True, check_range)


    def test_init_args(self):
        """
        Test creation of the argument parser
        """
        p = yg.init_args()
        self.assertTrue(isinstance(p, argparse.ArgumentParser))


    def test_handle_missing_start_date_arg(self):
        """
        Test the argument handler end range only
        """
        args = argparse.Namespace()
        args.end_date = '9999-12-31'
        args.template_file_name = __file__
        with self.assertRaises(yg.DateRangeArgError):
            yg.handle_args(args)


    def test_handle_missing_end_date_arg(self):
        """
        Test the argument handler start range only
        """
        args = argparse.Namespace()
        args.start_date = '9999-12-31'
        args.template_file_name = __file__
        with self.assertRaises(yg.DateRangeArgError):
            yg.handle_args(args)


    def test_handle_args_date_range(self):
        """
        Test the argument handler start and end range
        """
        args = argparse.Namespace()
        args.start_date = '9999-12-31'
        args.end_date = '9999-12-31'
        args.template_file_name = __file__
        yg.handle_args(args)
        self.assertTrue(isinstance(args.start_date, date))
        self.assertTrue(isinstance(args.end_date, date))


    def test_unfindable_args_template_file(self):
        """
        Test unfindable template file
        """
        args = argparse.Namespace()
        args.template_file_name = '\b'
        with self.assertRaises(FileNotFoundError):
            yg.handle_args(args)


    def test_unfindable_args_config_file(self):
        """
        Test unfindable config file
        """
        args = argparse.Namespace()
        args.config_file_name = '\b'
        args.template_file_name = __file__
        with self.assertRaises(FileNotFoundError):
            yg.handle_args(args)


    def test_zero_num_nodes_arg(self):
        """
        Test zero num_nodes arg
        """
        args = argparse.Namespace()

        args.template_file_name = __file__
        args.num_nodes = 0
        args = yg.handle_args(args)
        self.assertTrue(args.num_nodes is None)


    def test_negative_num_nodes_arg(self):
        """
        Test negative num_nodes arg
        """
        args = argparse.Namespace()

        args.template_file_name = __file__
        args.num_nodes = -1
        args = yg.handle_args(args)
        self.assertTrue(args.num_nodes is None)


    def test_positive_num_nodes_arg(self):
        """
        Test positive num_nodes arg
        """
        args = argparse.Namespace()

        args.template_file_name = __file__
        args.num_nodes = 10
        args = yg.handle_args(args)
        self.assertEqual(args.num_nodes, 10)


    def test_init_config(self):
        """
        Test configuration initialization
        """
        import yaml

        test_template_file_name = os.path.join(FILE_DIR, 'test_yaml_generator_template.yml.j2')
        test_config_file_name = os.path.join(FILE_DIR, 'test_yaml_generator_config.yml')
        config_file_data = yaml.safe_load(open(test_config_file_name, 'rt'))

        args = argparse.Namespace()
        args.template_file_name = test_template_file_name
        args.config_file_name = test_config_file_name
        args.start_date = date.today()
        args.end_date = date.today()
        args.random = False

        config = yg.init_config(args)

        for k in config_file_data.keys():
            if k.endswith('date'):
                self.assertEqual(config[k], getattr(args, k))
            else:
                self.assertEqual(config[k], config_file_data[k])


    def test_process_template(self):
        """ Test process jinja template """
        test_template_file_name = os.path.join(FILE_DIR, 'test_yaml_generator_template.yml.j2')
        test_config_file_name = os.path.join(FILE_DIR, 'test_yaml_generator_config.yml')
        test_output_file_name = os.path.join(FILE_DIR, 'test_ocp_generated.yml')
        config = yg.default_config()

        if os.path.exists(test_output_file_name):
            os.unlink(test_output_file_name)
        
        args = argparse.Namespace()
        args.template_file_name = test_template_file_name
        args.output_file_name = test_output_file_name
        args.config_file_name = test_config_file_name
        args.random = False

        yg.process_template(args, config)
        self.assertTrue(os.path.exists(test_output_file_name))
        os.unlink(test_output_file_name)

