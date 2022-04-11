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
"""Utility to generate koku-nise Azure yaml files"""
import os
import random
from calendar import monthrange
from datetime import date
from uuid import uuid4

import faker
from dateutil.relativedelta import relativedelta
from nise.util import LOG
from nise.yaml_generators.generator import Generator
from nise.yaml_generators.utils import dicta
from nise.yaml_generators.utils import generate_name


FAKER = faker.Faker()
ACCTS_STR = {
    "sql": ("Microsoft.Sql", "servers"),
    "storage": ("Microsoft.Storage", "storageAccounts"),
    "vmachine": ("Microsoft.Compute", "virtualMachines"),
    "vnetwork": ("Microsoft.Network", "publicIPAddresses"),
}
RESOURCE_LOCATIONS = [
    "US East",
    "US North Central",
    "US South Central",
    "US West 2",
    "US East 2",
    "US Central",
    "US West",
]
TAG_KEYS = {
    "bandwidth": ["environment", "version", "app"],
    "sql": ["environment", "version", "app"],
    "storage": ["environment", "version", "app", "storageclass"],
    "vmachine": ["environment", "version", "app"],
    "vnetwork": ["environment", "version", "app"],
}


def generate_instance_id(key, config, node_name=None):
    """Generate properly formatted instance_id."""
    resource_group, resource_name = FAKER.words(2)
    if node_name:
        resource_name = node_name
    if ACCTS_STR.get(key):
        consumed, second_part = ACCTS_STR.get(key)
    else:
        consumed, second_part = random.choice(list(ACCTS_STR.values()))
    resource_type = consumed + "/" + second_part
    accts_str = "/providers/" + resource_type + "/"
    return f"subscriptions/{config.payer_account}/resourceGroups/{resource_group}/{accts_str[1:-2]}/{resource_name}"


def generate_tags_and_instance_id(key, config, prefix="", suffix="", dynamic=True):
    """Generate properly formatted Azure tags and instance_id.

    Args:
        config.id_labels = {(resource_id, node_name): tags} or None
    Returns:
        tags (list), instance_id (str)
    """
    if not config.get("id_labels"):
        keys = TAG_KEYS.get(key)
        tags = [dicta(key=key, v=generate_name(config)) for key in keys]
        instance_id = generate_instance_id(key, config)
    else:
        id_label_key = random.choice(list(config.id_labels.keys()))
        tag_key_list = random.choice(config.id_labels.get(id_label_key))
        SEEN_KEYS = set()
        tags = []
        for key, value in tag_key_list:
            if key not in SEEN_KEYS:
                tags.append(dicta(key=key, v=value))
                SEEN_KEYS.update([key])
        _, node_name = id_label_key
        instance_id = generate_instance_id(key, config, node_name)
    return tags, instance_id


def generate_azure_dicta(config, key):
    """Return dicta with common attributes."""
    tags, instance_id = generate_tags_and_instance_id(key, config)
    rate = round(random.uniform(0.1, 0.50), 5)
    usage = round(random.uniform(0.01, 1), 5)

    return dicta(
        start_date=str(config.start_date),
        end_date=str(config.end_date),
        instance_id=instance_id,
        meter_id=str(uuid4()),
        resource_location=random.choice(RESOURCE_LOCATIONS),
        usage_quantity=usage,
        resource_rate=rate,
        pre_tax_cost=usage * rate,
        tags=tags,
    )


class AzureGenerator(Generator):
    """YAML generator for Azure."""

    def __init__(self, id_labels=None):
        self.id_labels = id_labels

    def init_config(self, args):
        """Process provider specific args."""
        config = super().init_config(args)

        # insert specific config variables

        config.id_labels = self.id_labels if self.id_labels else None

        return config

    def build_data(self, config, _random=False):  # noqa: C901
        """ """
        LOG.info("Data build starting")

        data = dicta(
            payer=config.payer_account,
            bandwidth_gens=[],
            sql_gens=[],
            storage_gens=[],
            vmachine_gens=[],
            vnetwork_gens=[],
        )

        max_bandwidth_gens = FAKER.random_int(0, config.max_bandwidth_gens) if _random else config.max_bandwidth_gens
        max_sql_gens = FAKER.random_int(0, config.max_sql_gens) if _random else config.max_sql_gens
        max_storage_gens = FAKER.random_int(0, config.max_storage_gens) if _random else config.max_storage_gens
        max_vmachine_gens = FAKER.random_int(0, config.max_vmachine_gens) if _random else config.max_vmachine_gens
        max_vnetwork_gens = FAKER.random_int(0, config.max_vnetwork_gens) if _random else config.max_vnetwork_gens

        LOG.info(f"Building {max_bandwidth_gens} Bandwidth generators ...")
        for _ in range(max_bandwidth_gens):
            data.bandwidth_gens.append(generate_azure_dicta(config, "bandwidth"))

        LOG.info(f"Building {max_sql_gens} SQL generators ...")
        for _ in range(max_sql_gens):
            data.sql_gens.append(generate_azure_dicta(config, "sql"))

        LOG.info(f"Building {max_storage_gens} Storage generators ...")
        for _ in range(max_storage_gens):
            data.storage_gens.append(generate_azure_dicta(config, "storage"))

        LOG.info(f"Building {max_vmachine_gens} Virtual Machine generators ...")
        for _ in range(max_vmachine_gens):
            data.vmachine_gens.append(generate_azure_dicta(config, "vmachine"))

        LOG.info(f"Building {max_vnetwork_gens} Virtual Network generators ...")
        for _ in range(max_vnetwork_gens):
            data.vnetwork_gens.append(generate_azure_dicta(config, "vnetwork"))

        return data

    def default_config(self):
        """
        Generate a config object with all values set to defaults
        Returns:
            dicta
        """
        default_date = date.today()
        last_day_of_month = monthrange(default_date.year, default_date.month)[1]
        return dicta(
            payer_account="657f539b-7f89-4b2c-8833-f73a4654a3bc",
            start_date=default_date.replace(day=1) - relativedelta(months=1),
            end_date=default_date.replace(day=last_day_of_month),
            max_name_words=2,
            max_resource_id_length=10,
            max_bandwidth_gens=1,
            max_sql_gens=1,
            max_storage_gens=1,
            max_vmachine_gens=1,
            max_vnetwork_gens=1,
        )

    def validate_config(self, config):
        """
        Validates that all known parts of a config are the required types
        Params:
            config : dicta - the configuration to test
        Returns:
            bool
        """
        validator = dicta(
            payer_account=str,
            start_date=date,
            end_date=date,
            storage_classes=list,
            max_name_words=int,
            max_resource_id_length=int,
            max_bandwidth_gens=int,
            max_sql_gens=int,
            max_storage_gens=int,
            max_vmachine_gens=int,
            max_vnetwork_gens=int,
        )
        result = [
            f"{k} Must be of type {validator[k].__name__}"
            for k in validator
            if k in config and not isinstance(config[k], validator[k])
        ]
        if result:
            raise TypeError(os.linesep.join(result))

        return True
