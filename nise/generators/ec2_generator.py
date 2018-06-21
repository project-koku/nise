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

from nise.generators.generator import AbstractGenerator


# pylint: disable=too-few-public-methods
class EC2Generator(AbstractGenerator):
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

    def _get_instance_type(self):
        """Pick random instance type."""
        return choice(self.INSTANCE_TYPES)

    def _get_processor_arch(self):
        """Pick instance architectures."""
        return choice(self.ARCHS)

    # pylint: disable=too-many-locals,too-many-statements
    def _update_data(self, row, start, end):
        """Update data with generator specific data."""
        inst_type, vcpu, memory, storage, family, cost, rate, description = \
            self._get_instance_type()
        inst_description = description.format(cost, inst_type)
        location, avail_zone, _ = self._get_location()
        row = self._add_common_usage_info(row, start, end)

        row['lineItem/ProductCode'] = 'AmazonEC2'
        row['lineItem/UsageType'] = 'BoxUsage:{}'.format(inst_type)
        row['lineItem/Operation'] = 'RunInstances'
        row['lineItem/AvailabilityZone'] = avail_zone
        row['lineItem/ResourceId'] = 'i-{}'.format(self.fake.ean8())  # pylint: disable=no-member
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
        row['product/processorFeatures'] = 'Intel AVX; Intel Turbo'
        row['product/productFamily'] = 'Compute Instance'
        row['product/servicecode'] = 'AmazonEC2'
        row['product/sku'] = self.fake.pystr(min_chars=12, max_chars=12).upper()  # pylint: disable=no-member
        row['product/storage'] = storage
        row['product/tenancy'] = 'Shared'
        row['product/usagetype'] = 'BoxUsage:{}'.format(inst_type)
        row['product/vcpu'] = vcpu
        row['pricing/publicOnDemandCost'] = cost
        row['pricing/publicOnDemandRate'] = rate
        row['pricing/term'] = 'OnDemand'
        row['pricing/unit'] = 'Hrs'
        return row

    def generate_data(self):
        """Responsibile for generating data."""
        data = []
        num_instances = randint(2, 60)
        for instance in range(0, num_instances):  # pylint: disable=W0612
            data += self._generate_hourly_data()
        return data
