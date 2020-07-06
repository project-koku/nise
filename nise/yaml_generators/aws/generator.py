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
"""Utility to generate koku-nise AWS yaml files."""
import os
import random
import re
from calendar import monthrange
from datetime import date
from random import uniform

import faker
from dateutil.relativedelta import relativedelta
from nise.util import LOG
from nise.yaml_generators.aws.ec2_instance_types import INSTANCE_TYPES as EC2_INSTANCES
from nise.yaml_generators.aws.rds_instance_types import INSTANCE_TYPES as RDS_INSTANCES
from nise.yaml_generators.aws.regions import REGIONS
from nise.yaml_generators.generator import Generator
from nise.yaml_generators.utils import dicta
from nise.yaml_generators.utils import generate_account_id
from nise.yaml_generators.utils import generate_name

SEEN_NAMES = set()
SEEN_RESOURCE_IDS = set()

DBL_DASH = re.compile("-+")
FAKER = faker.Faker()
RESOURCE_TAG_COLS = {
    "DTG": ["resourceTags/user:app"],
    "EBS": ["resourceTags/user:storageclass"],
    "EC2": ["resourceTags/user:environment", "resourceTags/user:version"],
    "RDS": ["resourceTags/user:app"],
    "R53": ["resourceTags/user:app"],
    "S3": ["resourceTags/user:storageclass"],
    "VPC": ["resourceTags/user:app"],
}


def uniform_yield(a, b):
    """Yield from random.uniform."""
    while True:
        yield uniform(a, b)


RATE_AMT = {
    "DTG": (uniform_yield(0.12, 0.19), uniform_yield(0.000002, 0.09)),
    "EBS": (uniform_yield(0.02, 0.16), uniform_yield(0.2, 300.99)),
    "S3": (uniform_yield(0.02, 0.06), uniform_yield(0.2, 6000.99)),
}


def generate_tags(key, config, prefix="", suffix="", dynamic=True):
    """Generate properly formatted AWS tags.

    Returns:
        list
    """
    keys = RESOURCE_TAG_COLS.get(key)
    return [dicta(key=key, v=generate_name(config)) for key in keys]


def generate_resource_id_and_tag(config, key):
    """Generate properly formatted AWS tags and resource_id.

    Args:
        config.id_labels = {(resource_id, node_name): tags} or None
    Returns:
        resource_id (str), tags (list)
    """
    if not config.get("id_labels"):
        resource_id = FAKER.ean8()
        tags = generate_tags(key, config)
    else:
        id_label_key = random.choice(list(config.id_labels.keys()))
        tag_key_list = random.choice(config.id_labels.get(id_label_key))
        SEEN_KEYS = set()
        tags = []
        for key, value in tag_key_list:
            if key not in SEEN_KEYS:
                tags.append(dicta(key=f"resourceTags/user:{key}", v=value))
                SEEN_KEYS.update([key])
        resource_id, _ = id_label_key
    return resource_id, tags


def initialize_dicta(key, config):
    """Return dicta with common attributes."""
    resource_id, tags = generate_resource_id_and_tag(config, key)
    return dicta(
        start_date=str(config.start_date),
        end_date=str(config.end_date),
        resource_id=resource_id,
        product_sku=FAKER.pystr(min_chars=12, max_chars=12).upper(),
        tags=tags,
    )


class AWSGenerator(Generator):
    """YAML generator for AWS."""

    def __init__(self, id_labels=None):
        self.id_labels = id_labels

    def init_config(self, args):
        """Process provider specific args."""
        config = super().init_config(args)

        # insert specific config variables

        config.id_labels = self.id_labels if self.id_labels else None

        return config

    def build_data(self, config, _random=False):  # noqa: C901
        """Build the data."""
        LOG.info("Data build starting")

        data = dicta(
            payer=config.payer_account,
            data_transfer_gens=[],
            ebs_gens=[],
            ec2_gens=[],
            rds_gens=[],
            route53_gens=[],
            s3_gens=[],
            vpc_gens=[],
            users=[],
        )

        max_data_transfer_gens = (
            FAKER.random_int(0, config.max_data_transfer_gens) if _random else config.max_data_transfer_gens
        )
        max_ebs_gens = FAKER.random_int(0, config.max_ebs_gens) if _random else config.max_ebs_gens
        max_ec2_gens = FAKER.random_int(0, config.max_ec2_gens) if _random else config.max_ec2_gens
        max_rds_gens = FAKER.random_int(0, config.max_rds_gens) if _random else config.max_rds_gens
        max_route53_gens = FAKER.random_int(0, config.max_route53_gens) if _random else config.max_route53_gens
        max_s3_gens = FAKER.random_int(0, config.max_s3_gens) if _random else config.max_s3_gens
        max_vpc_gens = FAKER.random_int(0, config.max_vpc_gens) if _random else config.max_vpc_gens
        max_users = FAKER.random_int(0, config.max_users) if _random else config.max_users

        LOG.info(f"Building {max_data_transfer_gens} data transfer generators ...")
        for _ in range(max_data_transfer_gens):
            _rate, _amount = RATE_AMT.get("DTG")
            data_transfer_gen = initialize_dicta("DTG", config)
            data_transfer_gen.update(amount=round(next(_amount), 5), rate=round(next(_rate), 5))
            data.data_transfer_gens.append(data_transfer_gen)

        LOG.info(f"Building {max_ebs_gens} EBS generators ...")
        for _ in range(max_ebs_gens):
            _rate, _amount = RATE_AMT.get("EBS")
            ebs_gen = initialize_dicta("EBS", config)
            ebs_gen.update(amount=round(next(_amount), 5), rate=round(next(_rate), 5))
            data.ebs_gens.append(ebs_gen)

        LOG.info(f"Building {max_ec2_gens} EC2 generators ...")
        for _ in range(max_ec2_gens):
            instance_type = random.choice(EC2_INSTANCES)
            ec2_gen = initialize_dicta("EC2", config)
            ec2_gen.update(
                processor_arch=instance_type.get("processor_arch"),
                region=random.choice(REGIONS),
                instance_type=instance_type,
            )
            data.ec2_gens.append(ec2_gen)

        LOG.info(f"Building {max_rds_gens} RDS generators ...")
        for _ in range(max_rds_gens):
            instance_type = random.choice(RDS_INSTANCES)
            rds_gen = initialize_dicta("RDS", config)
            rds_gen.update(
                processor_arch=instance_type.get("processor_arch"),
                region=random.choice(REGIONS),
                instance_type=instance_type,
            )
            data.rds_gens.append(rds_gen)

        LOG.info(f"Building {max_route53_gens} Route 53 generators ...")
        for _ in range(max_route53_gens):
            route53_gen = initialize_dicta("R53", config)
            route53_gen.update(product_family=random.choices(("DNS Zone", "DNS Query"), weights=[1, 10])[0])
            data.route53_gens.append(route53_gen)

        LOG.info(f"Building {max_s3_gens} S3 generators ...")
        for _ in range(max_s3_gens):
            _rate, _amount = RATE_AMT.get("S3")
            s3_gen = initialize_dicta("S3", config)
            s3_gen.update(amount=round(next(_amount), 5), rate=round(next(_rate), 5))
            data.s3_gens.append(s3_gen)

        LOG.info(f"Building {max_vpc_gens} VPC generators ...")
        for _ in range(max_vpc_gens):
            vpc_gen = initialize_dicta("VPC", config)
            data.vpc_gens.append(vpc_gen)

        LOG.info(f"Adding {max_users} users.")
        for _ in range(max_users):
            data.users.append(generate_account_id(config))

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
            payer_account=9999999999999,
            max_account_id_length=13,
            max_users=1,
            max_name_words=2,
            max_resource_id_length=10,
            max_data_transfer_gens=1,
            max_ebs_gens=1,
            max_ec2_gens=1,
            max_rds_gens=1,
            max_route53_gens=1,
            max_s3_gens=1,
            max_vpc_gens=1,
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
            payer_account=int,
            max_account_id_length=int,
            max_users=int,
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
