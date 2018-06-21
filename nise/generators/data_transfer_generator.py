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
"""Module for ebs data generation."""
from random import choice, uniform

from nise.generators.generator import AbstractGenerator


class DataTransferGenerator(AbstractGenerator):
    """Generator for Data Transfer data."""

    DATA_TRANSFER = (
        ('{}-{}-AWS-In-Bytes', 'PublicIP-In', 'InterRegion Inbound'),
        ('{}-{}-AWS-Out-Bytes', 'PublicIP-Out', 'InterRegion Outbound'),
    )

    def _get_data_transfer(self, rate):
        """Get data transfer info."""
        location1, _, storage_region1 = self._get_location()
        location2, _, storage_region2 = self._get_location()
        trans_desc, operation, trans_type = choice(self.DATA_TRANSFER)
        trans_desc = trans_desc.format(storage_region1, storage_region2)
        description = '${} per GB - {} data transfer to {}'.format(rate, location1, location2)
        return trans_desc, operation, description, location1, location2, trans_type

    def _update_data(self, row, start, end):
        """Update data with generator specific data."""
        row = self._add_common_usage_info(row, start, end)

        rate = round(uniform(0.12, 0.19), 3)
        amount = uniform(0.000002, 0.09)
        cost = amount * rate
        trans_desc, operation, description, location1, location2, trans_type = \
            self._get_data_transfer(rate)

        row['lineItem/ProductCode'] = 'AmazonEC2'
        row['lineItem/UsageType'] = trans_desc
        row['lineItem/Operation'] = operation
        row['lineItem/ResourceId'] = 'i-{}'.format(self.fake.ean8())  # pylint: disable=no-member
        row['lineItem/UsageAmount'] = str(amount)
        row['lineItem/CurrencyCode'] = 'USD'
        row['lineItem/UnblendedRate'] = str(rate)
        row['lineItem/UnblendedCost'] = str(cost)
        row['lineItem/BlendedRate'] = str(rate)
        row['lineItem/BlendedCost'] = str(cost)
        row['lineItem/LineItemDescription'] = description
        row['product/ProductName'] = 'Amazon Elastic Compute Cloud'
        row['product/location'] = location1
        row['product/locationType'] = 'AWS Region'
        row['product/productFamily'] = 'Data Transfer'
        row['product/servicecode'] = 'AWSDataTransfer'
        row['product/sku'] = self.fake.pystr(min_chars=12, max_chars=12).upper()  # pylint: disable=no-member
        row['product/toLocation'] = location2
        row['product/toLocationType'] = 'AWS Region'
        row['product/transferType'] = trans_type
        row['product/usagetype'] = trans_desc
        row['pricing/publicOnDemandCost'] = str(cost)
        row['pricing/publicOnDemandRate'] = str(rate)
        row['pricing/term'] = 'OnDemand'
        row['pricing/unit'] = 'GB'
        return row

    def _generate_hourly_data(self):
        """Create houldy data."""
        data = []
        for hour in self.hours:
            start = hour.get('start')
            end = hour.get('end')
            row = self._init_data_row(start, end)
            row = self._update_data(row, start, end)
            if self.fake.pybool():  # pylint: disable=no-member
                data.append(row)
        return data

    def generate_data(self):
        """Responsibile for generating data."""
        data = self._generate_hourly_data()
        return data
