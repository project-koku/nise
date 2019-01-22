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
"""Module for ec2 data generation."""
from random import choice, randint

from nise.generators.aws.aws_generator import AWSGenerator


# pylint: disable=too-few-public-methods
class EC2Generator(AWSGenerator):
    """Generator for EC2 data."""

    INSTANCE_TYPES = (
        ('m5.large', '2', '8 GiB', 'EBS Only', 'General Purpose',
         '0.096', '0.096', '${} per On Demand Linux {} Instance Hour'),
        ('c5d.2xlarge', '8', '16 GiB', '1 x 200 NVMe SSD', 'Compute Optimized',
         '0.34', '0.34', '${} per On Demand Linux {} Instance Hour'),
        ('c4.xlarge', '4', '7.5 GiB', 'EBS-Only', 'Compute Optimized',
         '0.199', '0.199', '${} per On Demand Linux {} Instance Hour'),
        ('r4.large', '2', '15.25 GiB', 'EBS-Only', 'Memory Optimized',
         '0.133', '0.133', '${} per On Demand Linux {} Instance Hour')
    )

    ARCHS = ('32-bit', '64-bit')

    def __init__(self, start_date, end_date, payer_account, usage_accounts, attributes):
        if attributes:
            self._processor_arch = attributes.get('processor_arch')
            self._resource_id = attributes.get('resource_id')
            self._product_sku = attributes.get('product_sku')
            self._tags = attributes.get('tags')
            self._instance_type = attributes.get('instance_type')

        super().__init__(start_date, end_date, payer_account, usage_accounts, attributes)

    def _get_instance_type(self):
        """Pick random instance type."""
        # inst_type, vcpu, memory, storage, family, cost, rate
        if self._instance_type:
            return (self._instance_type.get('inst_type'),
                    self._instance_type.get('vcpu'),
                    self._instance_type.get('memory'),
                    self._instance_type.get('storage'),
                    self._instance_type.get('family'),
                    self._instance_type.get('cost'),
                    self._instance_type.get('rate'),
                    '${} per On Demand Linux {} Instance Hour')
        else:
            return choice(self.INSTANCE_TYPES)

    def _get_processor_arch(self):
        """Pick instance architectures."""
        if self._processor_arch:
            return self._processor_arch
        else:
            return choice(self.ARCHS)

    def _get_resource_id(self):
        """Generate an instance id."""
        if self._resource_id:
            id = self._resource_id
        else:
            id = self.fake.ean8()  # pylint: disable=no-member
        return 'i-{}'.format(id)

    def _get_product_sku(self):
        """Generate product sku."""
        if self._product_sku:
            return self._product_sku
        else:
            return self.fake.pystr(min_chars=12, max_chars=12).upper()  # pylint: disable=no-member

    def _pick_tag(self, tag_key, options):
        """Generate tag from options."""
        if self._tags:
            return self._tags.get(tag_key)
        else:
            return choice(options)

    # pylint: disable=too-many-locals,too-many-statements
    def _update_data(self, row, start, end, **kwargs):
        """Update data with generator specific data."""
        inst_type, vcpu, memory, storage, family, cost, rate, description = \
            self._get_instance_type()
        inst_description = description.format(cost, inst_type)
        location, aws_region, avail_zone, _ = self._get_location()
        row = self._add_common_usage_info(row, start, end)

        row['lineItem/ProductCode'] = 'AmazonEC2'
        row['lineItem/UsageType'] = 'BoxUsage:{}'.format(inst_type)
        row['lineItem/Operation'] = 'RunInstances'
        row['lineItem/AvailabilityZone'] = avail_zone
        row['lineItem/ResourceId'] = self._get_resource_id()
        row['lineItem/UsageAmount'] = '1'
        row['lineItem/CurrencyCode'] = 'USD'
        row['lineItem/UnblendedRate'] = rate
        row['lineItem/UnblendedCost'] = cost
        row['lineItem/BlendedRate'] = rate
        row['lineItem/BlendedCost'] = cost
        row['lineItem/LineItemDescription'] = inst_description
        row['product/ProductName'] = 'Amazon Elastic Compute Cloud'
        row['product/clockSpeed'] = '2.8 GHz'
        row['product/currentGeneration'] = 'Yes'
        row['product/ecu'] = '14'
        row['product/enhancedNetworkingSupported'] = 'Yes'
        row['product/instanceFamily'] = family
        row['product/instanceType'] = inst_type
        row['product/licenseModel'] = 'No License required'
        row['product/location'] = location
        row['product/locationType'] = 'AWS Region'
        row['product/memory'] = memory
        row['product/networkPerformance'] = 'Moderate'
        row['product/operatingSystem'] = 'Linux'
        row['product/operation'] = 'RunInstances'
        row['product/physicalProcessor'] = 'Intel Xeon Family'
        row['product/preInstalledSw'] = 'NA'
        row['product/processorArchitecture'] = self._get_processor_arch()
        row['product/processorFeatures'] = 'Intel AVX Intel Turbo' #  fix this?
        row['product/productFamily'] = 'Compute Instance'
        row['product/region'] = aws_region
        row['product/servicecode'] = 'AmazonEC2'
        row['product/sku'] = self._get_product_sku()
        row['product/storage'] = storage
        row['product/tenancy'] = 'Shared'
        row['product/usagetype'] = 'BoxUsage:{}'.format(inst_type)
        row['product/vcpu'] = vcpu
        row['pricing/publicOnDemandCost'] = cost
        row['pricing/publicOnDemandRate'] = rate
        row['pricing/term'] = 'OnDemand'
        row['pricing/unit'] = 'Hrs'
        row['resourceTags/user:environment'] = self._pick_tag('resourceTags/user:environment', ('dev', 'ci', 'qa', 'stage', 'prod'))
        row['resourceTags/user:version'] = self._pick_tag('resourceTags/user:version', ('alpha', 'beta'))
        return row

    def generate_data(self):
        """Responsibile for generating data."""
        data = []
        num_instances = self.num_instances
        for instance in range(0, num_instances):  # pylint: disable=W0612
            data += self._generate_hourly_data()
        return data
