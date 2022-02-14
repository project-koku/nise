#
# Copyright 2018 Red Hat, Inc.
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
"""Module for aws data generators."""
from nise.generators.aws.aws_constants import REGIONS  # noqa: F401
from nise.generators.aws.aws_generator import AWSGenerator  # noqa: F401
from nise.generators.aws.data_transfer_generator import DataTransferGenerator  # noqa: F401
from nise.generators.aws.ebs_generator import EBSGenerator  # noqa: F401
from nise.generators.aws.ec2_generator import EC2Generator  # noqa: F401
from nise.generators.aws.marketplace_generator import MarketplaceGenerator  # noqa: F401
from nise.generators.aws.rds_generator import RDSGenerator  # noqa: F401
from nise.generators.aws.route53_generator import Route53Generator  # noqa: F401
from nise.generators.aws.s3_generator import S3Generator  # noqa: F401
from nise.generators.aws.vpc_generator import VPCGenerator  # noqa: F401
