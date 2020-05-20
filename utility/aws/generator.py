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
"""Utility to generate koku-nise AWS yaml files"""
import logging
import os
import random
import re
from calendar import monthrange
from datetime import date

import faker
from dateutil.relativedelta import relativedelta

from ..utility.gen import Generator
from ..utility.utils import dicta
from .ec2_instance_types import INSTANCE_TYPES as EC2_INSTANCES
from .rds_instance_types import INSTANCE_TYPES as RDS_INSTANCES
from .regions import REGIONS

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


def generate_tags(config, prefix="", suffix="", dynamic=True):
    return [generate_name(config) for _ in range(config.max_tags)]


class AWSGenerator(Generator):
    def build_data(self, config, _random=False):  # noqa: C901
        """

        """
        LOG.info("Data build starting")

        data = dicta(
            data_transfer_gens=[], ebs_gens=[], ec2_gens=[], rds_gens=[], route53_gens=[], s3_gens=[], vpc_gens=[]
        )

        max_data_transfer_gens = (
            FAKER.random_int(1, config.max_data_transfer_gens) if _random else config.max_data_transfer_gens
        )
        max_ebs_gens = FAKER.random_int(1, config.max_ebs_gens) if _random else config.max_ebs_gens
        max_ec2_gens = FAKER.random_int(1, config.max_ec2_gens) if _random else config.max_ec2_gens
        max_rds_gens = FAKER.random_int(1, config.max_rds_gens) if _random else config.max_rds_gens
        max_route53_gens = FAKER.random_int(1, config.max_route53_gens) if _random else config.max_route53_gens
        max_s3_gens = FAKER.random_int(1, config.max_s3_gens) if _random else config.max_s3_gens
        max_vpc_gens = FAKER.random_int(1, config.max_vpc_gens) if _random else config.max_vpc_gens

        for gen in range(max_data_transfer_gens):
            LOG.info(f"Building data transfer generator {gen + 1}/{max_data_transfer_gens}...")
            data_transfer_gen = dicta(
                start_date=str(config.start_date),
                end_date=str(config.end_date),
                resource_id=generate_resource_id(config),
                tags=generate_tags(config),
            )
            data.data_transfer_gens.append(data_transfer_gen)

        for gen in range(max_ebs_gens):
            LOG.info(f"Building EBS generator {gen + 1}/{max_ebs_gens}...")
            ebs_gen = dicta(
                start_date=str(config.start_date), end_date=str(config.end_date), tags=generate_tags(config)
            )
            data.ebs_gens.append(ebs_gen)

        for gen in range(max_ec2_gens):
            LOG.info(f"Building EC2 generator {gen + 1}/{max_ec2_gens}...")

            instance_type = random.choice(EC2_INSTANCES)

            ec2_gen = dicta(
                start_date=str(config.start_date),
                end_date=str(config.end_date),
                processor_arch=instance_type.get("processor_arch"),
                resource_id=generate_resource_id(config),
                product_sku=FAKER.pystr(min_chars=12, max_chars=12).upper(),
                region=random.choice(REGIONS),
                tags=generate_tags(config),
                instance_type=instance_type,
            )
            data.ec2_gens.append(ec2_gen)

        for gen in range(max_rds_gens):
            LOG.info(f"Building RDS generator {gen + 1}/{max_rds_gens}...")

            instance_type = random.choice(RDS_INSTANCES)

            rds_gen = dicta(
                start_date=str(config.start_date),
                end_date=str(config.end_date),
                processor_arch=instance_type.get("processor_arch"),
                resource_id=generate_resource_id(config),
                product_sku=FAKER.pystr(min_chars=12, max_chars=12).upper(),
                region=random.choice(REGIONS),
                tags=generate_tags(config),
                instance_type=instance_type,
            )

            data.rds_gens.append(rds_gen)

        for gen in range(max_route53_gens):
            LOG.info(f"Building Route 53 generator {gen + 1}/{max_route53_gens}...")
            route53_gen = dicta(
                start_date=str(config.start_date), end_date=str(config.end_date), tags=generate_tags(config)
            )

            data.route53_gens.append(route53_gen)

        for gen in range(max_s3_gens):
            LOG.info(f"Building S3 generator {gen + 1}/{max_s3_gens}...")
            s3_gen = dicta(
                start_date=str(config.start_date), end_date=str(config.end_date), tags=generate_tags(config)
            )

            data.s3_gens.append(s3_gen)

        for gen in range(max_vpc_gens):
            LOG.info(f"Building VPC generator {gen + 1}/{max_vpc_gens}...")
            vpc_gen = dicta(
                start_date=str(config.start_date), end_date=str(config.end_date), tags=generate_tags(config)
            )

            data.vpc_gens.append(vpc_gen)

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
            start_date=default_date.replace(day=1) - relativedelta(months=1),
            end_date=default_date.replace(day=last_day_of_month),
            max_name_words=2,
            max_resource_id_length=10,
            max_data_transfer_gens=10,
            max_ebs_gens=10,
            max_ec2_gens=10,
            max_rds_gens=10,
            max_route53_gens=10,
            max_s3_gens=10,
            max_vpc_gens=10,
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
            start_date=date,
            end_date=date,
            storage_classes=list,
            max_name_words=int,
            max_resource_id_length=int,
            max_data_transfer_gens=int,
            max_ebs_gens=int,
            max_ec2_gens=int,
            max_rds_gens=int,
            max_route53_gens=int,
            max_s3_gens=int,
            max_vpc_gens=int,
        )
        result = [
            f"{k} Must be of type {validator[k].__name__}"
            for k in validator
            if k in config and not isinstance(config[k], validator[k])
        ]
        if result:
            raise TypeError(os.linesep.join(result))

        return True
