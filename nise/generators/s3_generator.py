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
"""Module for s3 data generation."""
from random import uniform

from nise.generators.generator import AbstractGenerator


class S3Generator(AbstractGenerator):
    """Generator for S3 data."""

    def _get_arn(self, avail_zone):
        """Create an amazon resource name."""
        arn = 'arn:aws:ec2:{}:{}:snapshot/snap-{}'.format(avail_zone,
                                                          self.payer_account,
                                                          self.fake.ean8())  # pylint: disable=no-member
        return arn

    def _update_data(self, row, start, end):
        """Update data with generator specific data."""
        row = self._add_common_usage_info(row, start, end)

        rate = round(uniform(0.02, 0.06), 3)
        amount = uniform(0.2, 6000.99)
        cost = amount * rate
        location, aws_region, avail_zone, storage_region = self._get_location()
        description = '${} per GB-Month of snapshot data stored - {}'.format(rate, location)
        amazon_resource_name = self._get_arn(avail_zone)

        row['lineItem/ProductCode'] = 'AmazonEC2'
        row['lineItem/UsageType'] = '{}:SnapshotUsage'.format(storage_region)
        row['lineItem/Operation'] = 'CreateSnapshot'
        row['lineItem/ResourceId'] = amazon_resource_name
        row['lineItem/UsageAmount'] = str(amount)
        row['lineItem/CurrencyCode'] = 'USD'
        row['lineItem/UnblendedRate'] = str(rate)
        row['lineItem/UnblendedCost'] = str(cost)
        row['lineItem/BlendedRate'] = str(rate)
        row['lineItem/BlendedCost'] = str(cost)
        row['lineItem/LineItemDescription'] = description
        row['product/ProductName'] = 'Amazon Elastic Compute Cloud'
        row['product/location'] = location
        row['product/locationType'] = 'AWS Region'
        row['product/productFamily'] = 'Storage Snapshot'
        row['product/region'] = aws_region
        row['product/servicecode'] = 'AmazonEC2'
        row['product/sku'] = self.fake.pystr(min_chars=12, max_chars=12).upper()  # pylint: disable=no-member
        row['product/storageMedia'] = 'Amazon S3'
        row['product/usagetype'] = '{}:SnapshotUsage'.format(storage_region)
        row['pricing/publicOnDemandCost'] = str(cost)
        row['pricing/publicOnDemandRate'] = str(rate)
        row['pricing/term'] = 'OnDemand'
        row['pricing/unit'] = 'GB-Mo'
        return row

    def generate_data(self):
        """Responsibile for generating data."""
        data = self._generate_hourly_data()
        return data
