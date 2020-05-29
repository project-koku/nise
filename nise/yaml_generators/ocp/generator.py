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
"""Utility to generate koku-nise OCP yaml files."""
import logging
import os
import re
from calendar import monthrange
from datetime import date

import faker
from dateutil.relativedelta import relativedelta
from nise.yaml_generators.generator import Generator
from nise.yaml_generators.utils import dicta


LOG = logging.getLogger(__name__)

SEEN_NAMES = set()
SEEN_RESOURCE_IDS = set()

DBL_DASH = re.compile("-+")
FAKER = faker.Faker()


def generate_words(config):
    """
    Generate a hyphen-separated string of words.

    The number of words is specified in the config. (config.max_name_words)
    """
    return "-".join(FAKER.words(config.max_name_words))


def generate_number_str(config):
    """
    Generate a string of digits of arbitrary length.

    The maximum length is specified in the config. (config.max_resource_id_length)
    """
    return str(FAKER.random_int(0, 10 ** config.max_resource_id_length)).zfill(config.max_resource_id_length)


def generate_name(config, prefix="", suffix="", dynamic=True, generator=generate_words, cache=SEEN_NAMES):
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
            prefix += "-"
        if suffix:
            suffix = "-" + suffix
        mid = generator(config) if dynamic else ""
        new_name = f"{prefix}{mid}{suffix}"
        if new_name not in cache:
            cache.add(new_name)
            break

    return DBL_DASH.sub("-", new_name)


def generate_resource_id(config, prefix="", suffix="", dynamic=True):
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
    return generate_name(
        config, prefix=prefix, suffix=suffix, dynamic=dynamic, generator=generate_number_str, cache=SEEN_RESOURCE_IDS
    )


def generate_labels(num_labels):
    """
    Generate a string of pipe-separated label:var sets.

    Params:
        num_labels : int - number of label sets to generate

    Returns:
        str
    """
    return "|".join(f"label_{e[0]}:{e[1]}" for e in zip(FAKER.words(num_labels), FAKER.words(num_labels)))


class OCPGenerator(Generator):
    """YAML generator for OCP."""

    def build_data(self, config, _random=False):  # noqa: C901
        """
        Build a structure to fill out a nise yaml template.

        Struture has the form of:
            {start_date: date,    (config.start_date)
            ens_date: date,      (config.end_date)
            nodes: [             (number of nodes controlled by config.max_nodes)
                {node_name: str,     (dynamic)
                cpu_cores: int,     (config.max_node_cpu_cores)
                memory_gig: int,    (config.max_node_memory_gig)
                resource_id: str,   (dynamic)
                namespaces: [     (number of namespaces controlled by config.max_node_namespaces)
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
        LOG.info("Data build starting")

        data = dicta(start_date=str(config.start_date), end_date=str(config.end_date), nodes=[])

        if _random:
            max_nodes = FAKER.random_int(1, config.max_nodes)
        else:
            max_nodes = config.max_nodes

        for node_ix in range(max_nodes):
            LOG.info(f"Building node {node_ix + 1}/{max_nodes}...")
            if _random:
                cores = FAKER.random_int(1, config.max_node_cpu_cores)
                memory = FAKER.random_int(1, config.max_node_memory_gig)
            else:
                cores = config.max_node_cpu_cores
                memory = config.max_node_memory_gig

            node = dicta(
                name=generate_name(config),
                cpu_cores=cores,
                memory_gig=memory,
                resource_id=generate_resource_id(config),
                namespaces=[],
            )
            data.nodes.append(node)

            if _random:
                max_namespaces = FAKER.random_int(1, config.max_node_namespaces)
            else:
                max_namespaces = config.max_node_namespaces

            for namespace_ix in range(max_namespaces):
                LOG.info(f"Building node {node_ix + 1}/{max_nodes}; namespace {namespace_ix + 1}/{max_namespaces}...")

                namespace = dicta(name=generate_name(config, prefix=node.name), pods=[], volumes=[])
                node.namespaces.append(namespace)

                if _random:
                    max_pods = FAKER.random_int(1, config.max_node_namespace_pods)
                else:
                    max_pods = config.max_node_namespace_pods

                LOG.info(f"Building {max_pods} pods...")
                for pod_ix in range(max_pods):
                    if _random:
                        cpu_req = FAKER.random_int(1, node.cpu_cores)
                        mem_req = FAKER.random_int(1, node.memory_gig)
                        cpu_lim = FAKER.random_int(1, node.cpu_cores)
                        mem_lim = FAKER.random_int(1, node.memory_gig)
                        pod_sec = FAKER.random_int(
                            config.min_node_namespace_pod_seconds,
                            config.max_node_namespace_pod_seconds,
                            step=(config.max_node_namespace_pod_seconds // 10) or 1800,
                        )
                    else:
                        cpu_lim = cpu_req = node.cpu_cores
                        mem_lim = mem_req = node.memory_gig
                        pod_sec = config.max_node_namespace_pod_seconds

                    pod = dicta(
                        name=generate_name(config, prefix=namespace.name + "-pod", suffix=str(pod_ix), dynamic=False),
                        cpu_request=cpu_req,
                        mem_request_gig=mem_req,
                        cpu_limit=cpu_lim,
                        mem_limit_gig=mem_lim,
                        pod_seconds=pod_sec,
                        labels=generate_labels(config.max_node_namespace_pod_labels),
                    )
                    namespace.pods.append(pod)

                if _random:
                    max_volumes = FAKER.random_int(1, config.max_node_namespace_volumes)
                else:
                    max_volumes = config.max_node_namespace_volumes

                LOG.info(f"Building {max_volumes} volumes...")
                for volume_ix in range(max_volumes):
                    if _random:
                        storage_cls = config.storage_classes[FAKER.random_int(0, len(config.storage_classes) - 1)]
                        vol_req = FAKER.random_int(1, config.max_node_namespace_volume_request_gig)
                    else:
                        storage_cls = config.storage_classes[0]
                        vol_req = config.max_node_namespace_volume_request_gig

                    volume = dicta(
                        name=generate_name(
                            config, prefix=namespace.name + "-vol", suffix=str(volume_ix), dynamic=False
                        ),
                        storage_class=storage_cls,
                        volume_request_gig=vol_req,
                        labels=generate_labels(config.max_node_namespace_volume_labels),
                        volume_claims=[],
                    )
                    namespace.volumes.append(volume)

                    if _random:
                        max_volume_claims = FAKER.random_int(1, config.max_node_namespace_volume_volume_claims)
                    else:
                        max_volume_claims = config.max_node_namespace_volume_volume_claims

                    for volume_claim_ix in range(max_volume_claims):
                        if _random:
                            cap = FAKER.random_int(1, config.max_node_namespace_volume_volume_claim_capacity_gig)
                        else:
                            cap = config.max_node_namespace_volume_volume_claim_capacity_gig

                        pod_name = namespace.pods[
                            -1 if volume_claim_ix >= len(namespace.pods) else volume_claim_ix
                        ].name
                        volume_claim = dicta(
                            name=generate_name(
                                config,
                                prefix=namespace.name + "-vol-claim",
                                suffix=str(volume_claim_ix),
                                dynamic=False,
                            ),
                            pod_name=pod_name,
                            labels=generate_labels(config.max_node_namespace_volume_volume_claim_labels),
                            capacity_gig=cap,
                        )
                        volume.volume_claims.append(volume_claim)

        return data

    def default_config(self):
        """
        Generate a config object with all values set to defaults.

        Returns:
            dicta
        """
        default_date = date.today()
        last_day_of_month = monthrange(default_date.year, default_date.month)[1]
        return dicta(
            start_date=default_date.replace(day=1) - relativedelta(months=1),
            end_date=default_date.replace(day=last_day_of_month),
            storage_classes=["gp2"],
            max_name_words=2,
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
            max_node_namespace_volume_volume_claim_capacity_gig=20,
        )

    def validate_config(self, config):
        """
        Validate that all known parts of a config are the required types.

        Params:
            config : dicta - the configuration to test

        Returns:
            bool
        """
        validator = dicta(
            start_date=date,
            end_date=date,
            storage_classes=list,
            max_name_words=int,
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
            max_node_namespace_volume_volume_claim_capacity_gig=int,
        )
        result = [
            f"{k} Must be of type {validator[k].__name__}"
            for k in validator
            if k in config and not isinstance(config[k], validator[k])
        ]
        if result:
            raise TypeError(os.linesep.join(result))

        return True
