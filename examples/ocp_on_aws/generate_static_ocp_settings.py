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
"""Utility to generate koku-nise OCP yaml files"""

from argparse import ArgumentParser, Namespace
from calendar import monthrange
from datetime import date
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
import faker
from jinja2 import Environment, FileSystemLoader
import logging
import os
import re
import sys
import time
from typing import Callable
import yaml


logging.basicConfig(stream=sys.stderr)
LOG = logging.getLogger(__name__)

SEEN_NAMES = set()
SEEN_RESOURCE_IDS = set()

DBL_DASH = re.compile('\-+')
FAKER = faker.Faker()


class DateRangeArgsError(Exception):
    pass


class dicta(dict):
    """
    Dict object that can access values via subscript or attribute
    This object is serializable just as a dict is.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __getattr__(self, key):
        return super().__getitem__(key)
    
    def __setattr__(self, key, val):
        super().__setitem__(key, val)
    
    def __delattr__(self, key):
        super().__delitem__(key)
    
    def copy(self):
        return self.__class__(self)


def generate_words(config : dicta) -> str:
    """
    Generate a hyphen-separated string of words.
    The number of words is specified in the config. (config.name_wordiness)
    """
    return '-'.join(FAKER.words(config.name_wordiness))


def generate_number_str(config : dicta) -> str :
    """
    Generate a string of digits of arbitrary length.
    The maximum length is specified in the config. (config.max_resource_id_length)
    """
    return str(FAKER.random_int(0, 10 ** config.max_resource_id_length)).zfill(config.max_resource_id_length)


def generate_name(config : dicta, prefix : str ='', suffix : str ='', dynamic : bool = True, generator : Callable = generate_words, cache : set = SEEN_NAMES) -> str :
    """
    Generate a random resource name using faker.
    Params:
        config : dicta - config information for the generator
        prefix : str - a static prefix
        suffix : str - a static suffix
        dynamic : bool - flag to run the generator function
        generator : func - function that will generate the dynamic portion of the name
        cache : set - a cache for uniqueness across all calls
    Returns:
        str
    """
    new_name = None
    while True:
        if prefix:
            prefix += '-'
        if suffix:
            suffix = '-' + suffix
        mid = generator(config) if dynamic else ''
        new_name = f'{prefix}{mid}{suffix}'
        if new_name not in cache:
            cache.add(new_name)
            break

    return DBL_DASH.sub('-', new_name)


def generate_resource_id(config : dicta, prefix : str = '', suffix : str = '', dynamic : bool = True) -> str :
    """
    Generate a random resource id using faker.
    Params:
        config : dicta - config information for the generator
        prefix : str - a static prefix
        suffix : str - a static suffix
        dynamic : bool - flag to run the generator function
        generator : func - function that will generate the dynamic portion of the resource id
        cache : set - a cache for uniqueness across all calls
    Returns:
        str
    """
    return generate_name(config, prefix=prefix, suffix=suffix, dynamic=dynamic, generator=generate_number_str, cache=SEEN_RESOURCE_IDS)


def generate_labels(num_labels : int) -> str :
    """
    Generate a string of pipe-separated label:var sets
    Params:
        num_labels : int - number of label sets to generate
    Returns:
        str
    """
    return '|'.join(f'label_{e[0]}:{e[1]}' for e in zip(FAKER.words(num_labels), FAKER.words(num_labels)))


def build_data(config : dicta) -> dicta :
    """
    Build a structure to fill out a nise yaml template
    Struture has the form of:
        {start_date: date,    (config.start_date)
         ens_date: date,      (config.end_date)
         nodes: [             (number of nodes controlled by config.max_nodes)
             {node_name: str,     (dynamic)
              cpu_cores: int,     (config.max_node_cpu_cores)
              memory_gig: int,    (config.max_node_memory_gig)
              resource_id: str,   (dynamic)
              <namespaces>: [     (namespace is dynamic. number of namespaces controlled by config.max_node_namespaces)
                  {namespace: str,   (dynamic)
                   pods: [           (number of pods controlled by config.max_node_namespace_pods)
                       pod_name: str,        (dynamic)
                       cpu_request: int,     (config.max_node_namespace_pod_cpu_request)
                       mem_request_gig: int, (config.max_node_namespace_pod_mem_request_gig)
                       cpu_limit: int,       (config.max_node_namespace_pod_cpu_limit)
                       mem_limit_gig: int,   (config.max_node_namespace_pod_mem_limit_gig)
                       pod_seconds: int,     (config.max_node_namespace_pod_seconds)
                       labels: str           (dynamic)
                   ],
                   volumes: [
                       volume_name: str,   
                       storage_class: str,
                       volume_request_gig: int,
                       labels: str,
                       volume_claims: [
                           volume_claim_name: str,
                           pod_name: str,
                           labels: str,
                           capacity_gig: int
                       ]
                   ]}
              ]}
         ]}
    Parameters:
        config : dicta
    Returns:
        dicta
    """

    print('Data build starting', file=sys.stderr)

    data = dicta(start_date=str(config.start_date), end_date=str(config.end_date), nodes=[])

    max_nodes = FAKER.random_int(1, config.max_nodes)
    for node_ix in range(max_nodes):
        print(f"Building node {node_ix}/{max_nodes}...", file=sys.stderr)

        node = dicta(name=generate_name(config), 
                     cpu_cores=FAKER.random_int(1, config.max_node_cpu_cores),
                     memory_gig=FAKER.random_int(1, config.max_node_memory_gig),
                     resource_id=generate_resource_id(config),
                     namespaces=[])
        data.nodes.append(node)

        max_namespaces = FAKER.random_int(1, config.max_node_namespaces)
        for namespace_ix in range(max_namespaces):
            print(f"Building node {node_ix}/{max_nodes}; namespace {namespace_ix}/{max_namespaces}...", file=sys.stderr)
            
            namespace = dicta(name=generate_name(config, prefix=node.name),
                              pods=[],
                              volumes=[])
            node.namespaces.append(namespace)

            max_pods = FAKER.random_int(1, config.max_node_namespace_pods)
            print(f"Building {max_pods} pods...", file=sys.stderr)
            for pod_ix in range(max_pods):
                pod = dicta(name=generate_name(config, 
                                               prefix=namespace.name + '-pod', 
                                               suffix=str(pod_ix), dynamic=False),
                            cpu_request=FAKER.random_int(1, node.cpu_cores),
                            mem_request_gig=FAKER.random_int(1, node.memory_gig),
                            cpu_limit=FAKER.random_int(1, node.cpu_cores),
                            mem_limit_gig=FAKER.random_int(1, node.memory_gig),
                            pod_seconds=FAKER.random_int(config.min_node_namespace_pod_seconds, 
                                                  config.max_node_namespace_pod_seconds, 
                                                  step=(config.max_node_namespace_pod_seconds // 10) or 1800),
                            labels=generate_labels(config.max_node_namespace_pod_labels))
                namespace.pods.append(pod)
            
            max_volumes = FAKER.random_int(1, config.max_node_namespace_volumes)
            print(f"Building {max_volumes} volumes...", file=sys.stderr)
            for volume_ix in range(max_volumes):
                volume = dicta(name=generate_name(config, 
                                                  prefix=namespace.name + '-vol', 
                                                  suffix=str(volume_ix), 
                                                  dynamic=False),
                            storage_class=config.storage_classes[FAKER.random_int(0, len(config.storage_classes) - 1)],
                            volume_request_gig=FAKER.random_int(1, config.max_node_namespace_volume_request_gig),
                            labels=generate_labels(config.max_node_namespace_volume_labels),
                            volume_claims=[])
                namespace.volumes.append(volume)

                for volume_claim_ix in range(FAKER.random_int(1, config.max_node_namespace_volume_volume_claims)):
                    pod_name = namespace.pods[-1 if volume_claim_ix >= len(namespace.pods) else volume_claim_ix].name
                    volume_claim = dicta(name=generate_name(config, 
                                                            prefix=namespace.name + '-vol-claim', 
                                                            suffix=str(volume_claim_ix), 
                                                            dynamic=False),
                                        pod_name=pod_name,
                                        labels=generate_labels(config.max_node_namespace_volume_volume_claim_labels),
                                        capacity_gig=FAKER.random_int(1, config.max_node_namespace_volume_volume_claim_capacity_gig))
                    volume.volume_claims.append(volume_claim)
    
    return data


def default_config() -> dicta :
    """
    Generate a config object with all values set to defaults
    Returns:
        dicta
    """
    default_date = date.today()
    last_day_of_month = monthrange(default_date.year, default_date.month)[1]
    return dicta(start_date=default_date.replace(day=1) - relativedelta(months=1),
                 end_date=default_date.replace(day=last_day_of_month),
                 storage_classes=['gp2'],
                 name_wordiness=2,
                 max_resource_id_length=10,
                 max_nodes=1,
                 max_node_cpu_cores=1,
                 max_node_memory_gig=2,
                 max_node_namespaces=1,
                 max_node_namespace_pods=1,
                 min_node_namespace_pod_seconds=300,
                 max_node_namespace_pod_seconds=3600,
                 max_node_namespace_pod_labels=1,
                 max_node_namespace_volumes=1,
                 max_node_namespace_volume_request_gig=20,
                 max_node_namespace_volume_labels=1,
                 max_node_namespace_volume_volume_claims=1,
                 max_node_namespace_volume_volume_claim_labels=1,
                 max_node_namespace_volume_volume_claim_capacity_gig=20)


def validate_config(config : dicta) -> bool :
    """
    Validates that all known parts of a config are the required types
    Params:
        config : dicta - the configuration to test
    Returns:
        bool
    """
    validator = dicta(start_date=date,
                      end_date=date,
                      storage_classes=list,
                      name_wordiness=int,
                      max_resource_id_length=int,
                      max_nodes=int,
                      max_node_cpu_cores=int,
                      max_node_memory_gig=int,
                      max_node_namespaces=int,
                      max_node_namespace_pods=int,
                      min_node_namespace_pod_seconds=int,
                      max_node_namespace_pod_seconds=int,
                      max_node_namespace_pod_labels=int,
                      max_node_namespace_volumes=int,
                      max_node_namespace_volume_request_gig=int,
                      max_node_namespace_volume_labels=int,
                      max_node_namespace_volume_volume_claims=int,
                      max_node_namespace_volume_volume_claim_labels=int,
                      max_node_namespace_volume_volume_claim_capacity_gig=int)
    result = [f'{k} Must be of type {validator[k].__name__}' for k in validator if k in config and not isinstance(config[k], validator[k])]
    if result:
        raise TypeError(os.linesep.join(result))
    
    return True


def init_args() -> ArgumentParser :
    """
    Initialize the argument parser.
    Returns:
        ArgumentParser
    """
    parser = ArgumentParser()
    parser.add_argument('-o', '--output', dest='output_file_name', type=str, required=False, metavar='FILE', help='Output file path.')
    parser.add_argument('-c', '--config', dest='config_file_name', type=str, required=False, metavar='CONF', help='Config file path.')
    parser.add_argument('-t', '--template', dest='template_file_name', type=str, required=True, metavar='TMPL', help='Template file path.')
    parser.add_argument('-s', '--start-date', dest='start_date', type=str, required=False, metavar='YYYY-MM-DD', help='Start date (overrides template, default is first day of last month)')
    parser.add_argument('-e', '--end-date', dest='end_date', type=str, required=False, metavar='YYYY-MM-DD', help='End date (overrides template, default is last day of current month)')
    parser.add_argument('-n', '--num-nodes', dest='num_nodes', type=int, required=False, metavar='INT', help='Number of nodes to generate (overrides template, default is 1)')

    return parser


def handle_args(args : Namespace) -> Namespace :
    """
    Parse and validate the arguments.
    Returns:
        Namespace
    """
    if not os.path.exists(args.template_file_name):
        raise FileNotFoundError(f'Cannot find file "{args.template_file_name}"')

    if int(bool(args.start_date)) + int(bool(args.end_date)) == 1:
        raise DateRangeArgsError("The full date range must be supplied or omitted.")
    
    if args.start_date:
        args.start_date = parse(args.start_date).date()
    if args.end_date:
        args.end_date = parse(args.end_date).date()
    
    if args.num_nodes and args.num_nodes < 1:
        args.num_nodes = None
    
    return args
    

def init_config(args : Namespace) -> dicta:
    """
    Initialize the config object for template processing.
    Params:
        args : Namespace - Command line arguments
    Returns:
        dicta - The initialized config object
    """
    config = default_config()

    if args.config_file_name:
        config_settings = yaml.safe_load(open(args.config_file_name, 'rt'))
        config.update(config_settings)
    
    if args.start_date:
        config.start_date = args.start_date
    if isinstance(config.start_date, str):
        config.start_date = parse(config.start_date)
    if args.end_date:
        config.end_date = args.end_date
    if isinstance(config.end_date, str):
        config.end_date = parse(config.end_date)
    if args.num_nodes:
        config.max_nodes = args.num_nodes
    
    validate_config(config)
    
    return config


def process_template(args : Namespace, config : dicta) -> None :
    """
    Process the jinja2 template using supplied parameter data.
    Produces an output file (if specified) or writes data to stdout.
    Parameters:
        args : Namespace - Command line arguments
        config : dicta - Template data generation config data
    Returns:
        None
    """
    data = build_data(config)

    template_file_name = os.path.abspath(args.template_file_name)
    template_loader = FileSystemLoader(os.path.dirname(template_file_name))
    env = Environment(loader=template_loader)
    template = env.get_template(os.path.basename(template_file_name))

    output = template.render(generator=data)

    if args.output_file_name == sys.stdout:
        sys.stdout.write(output)
        sys.stdout.flush()
    else:
        with open(args.output_file_name, 'wt') as outf:
            outf.write(output)
            outf.flush()


if __name__ == '__main__':
    args = handle_args(init_args().parse_args())
    config = init_config(args)
    process_template(args, config)
