#
# Copyright 2021 Red Hat, Inc.
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
"""Utility to generate koku-nise GCP yaml files."""
import os
import random
from calendar import monthrange
from datetime import date

import faker
from dateutil.relativedelta import relativedelta
from nise.util import LOG
from nise.yaml_generators.generator import Generator
from nise.yaml_generators.utils import dicta


FAKER = faker.Faker()

TAG_KEYS = {
    "compute": ["environment", "version", "app"],
    "storage": ["environment", "version", "app"],
    "network": ["environment", "version", "app"],
    "database": ["environment", "version", "app"],
}


def generate_gcp_dicta(config, key):
    """Return dicta with common attributes."""
    tags = generate_tags(key, config)
    cost = round(random.uniform(0.1, 0.50), 5)
    currency = "USD"
    return dicta(
        start_date=str(config.start_date), end_date=str(config.end_date), tags=tags, cost=cost, currency=currency
    )


def generate_tags(key, config):
    """generates the tags dictionary for gcp tags"""
    tags = dicta()
    if not config.get("tags"):
        keys = TAG_KEYS.get(key)
        for k in keys:
            tags[k] = FAKER.word()
    else:
        tag_key_list = random.choice(config.tags.get(key))
        SEEN_KEYS = set()
        tags = {}
        for k, v in tag_key_list.items():
            if k not in SEEN_KEYS:
                tags[k] = v
                SEEN_KEYS.update(k)
    return tags


class GCPGenerator(Generator):
    """YAML generator for GCP."""

    def __init__(self, tags=None):
        self.tags = tags

    def init_config(self, args):
        """Process provider specific args."""
        config = super().init_config(args)

        # insert specific config variables

        config.tags = self.tags if self.tags else None

        return config

    def default_config(self, *args, **kwargs):
        """
        Generate a config object with all values set to defaults
        Returns:
            dicta
        """
        default_date = date.today()
        last_day_of_month = monthrange(default_date.year, default_date.month)[1]
        return dicta(
            billing_account_id=FAKER.word() + "-" + FAKER.word(),
            project_id="not-a-project",
            project_name="not-a-project-name",
            start_date=default_date.replace(day=1) - relativedelta(months=1),
            end_date=default_date.replace(day=last_day_of_month),
            max_compute_gens=1,
            max_storage_gens=1,
            max_network_gens=1,
            max_database_gens=1,
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
            billing_account_id=str,
            project_name=str,
            project_id=str,
            max_compute_gens=int,
            max_database_gens=int,
            max_network_gens=int,
            max_storage_gens=int,
        )
        result = [
            f"{k} Must be of type {validator[k].__name__}"
            for k in validator
            if k in config and not isinstance(config[k], validator[k])
        ]
        if result:
            raise TypeError(os.linesep.join(result))

        return True

    def build_data(self, config, _random=False):
        """
        build the data
        """
        LOG.info("Data build starting")

        data = dicta(
            account_id=config.billing_account_id,
            project_id=config.project_id,
            project_name=config.project_name,
            compute_gens=[],
            storage_gens=[],
            network_gens=[],
            database_gens=[],
        )

        max_compute_gens = FAKER.random_int(0, config.max_compute_gens) if _random else config.max_compute_gens
        max_storage_gens = FAKER.random_int(0, config.max_storage_gens) if _random else config.max_storage_gens
        max_network_gens = FAKER.random_int(0, config.max_network_gens) if _random else config.max_network_gens
        max_database_gens = FAKER.random_int(0, config.max_database_gens) if _random else config.max_database_gens

        LOG.info(f"Building {max_compute_gens} Compute Engine generators ...")
        for _ in range(max_compute_gens):
            data.compute_gens.append(generate_gcp_dicta(config, "compute"))

        LOG.info(f"Building {max_storage_gens} Storage generators ...")
        for _ in range(max_storage_gens):
            data.storage_gens.append(generate_gcp_dicta(config, "storage"))

        LOG.info(f"Building {max_network_gens} Network generators ...")
        for _ in range(max_network_gens):
            data.network_gens.append(generate_gcp_dicta(config, "network"))

        LOG.info(f"Building {max_database_gens} Database generators ...")
        for _ in range(max_database_gens):
            data.database_gens.append(generate_gcp_dicta(config, "database"))
        return data
