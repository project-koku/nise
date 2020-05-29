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

from nise.generators.aws.aws_generator import AWSGenerator


class S3Generator(AWSGenerator):
    """Generator for S3 data."""

    def __init__(self, start_date, end_date, payer_account, usage_accounts, attributes=None):
        """Initialize the S3 generator."""
        super().__init__(start_date, end_date, payer_account, usage_accounts, attributes)
        self._amount = uniform(0.2, 6000.99)
        self._rate = round(uniform(0.02, 0.06), 3)
        self._product_sku = self.fake.pystr(min_chars=12, max_chars=12).upper()
        if self.attributes:
            if self.attributes.get("amount"):
                self._amount = self.attributes.get("amount")
            if self.attributes.get("rate"):
                self._rate = self.attributes.get("rate")
            if self.attributes.get("product_sku"):
                self._product_sku = self.attributes.get("product_sku")
            if self.attributes.get("tags"):
                self._tags = self.attributes.get("tags")

    def _get_arn(self, avail_zone):
        """Create an amazon resource name."""
        return "arn:aws:ec2:{}:{}:snapshot/snap-{}".format(avail_zone, self.payer_account, self.fake.ean8())

    def _update_data(self, row, start, end, **kwargs):
        """Update data with generator specific data."""
        row = self._add_common_usage_info(row, start, end)

        rate = self._rate
        amount = self._amount
        cost = amount * rate
        location, aws_region, avail_zone, _ = self._get_location()
        description = f"${rate} per GB-Month of snapshot data stored - {location}"
        amazon_resource_name = self._get_arn(avail_zone)

        row["lineItem/ProductCode"] = "AmazonS3"
        row["lineItem/UsageType"] = "Requests-Tier2"
        row["lineItem/Operation"] = "GetObject"
        row["lineItem/ResourceId"] = amazon_resource_name
        row["lineItem/UsageAmount"] = str(amount)
        row["lineItem/CurrencyCode"] = "USD"
        row["lineItem/UnblendedRate"] = str(rate)
        row["lineItem/UnblendedCost"] = str(cost)
        row["lineItem/BlendedRate"] = str(rate)
        row["lineItem/BlendedCost"] = str(cost)
        row["lineItem/LineItemDescription"] = description
        row["product/ProductName"] = "Amazon Simple Storage Service"
        row["product/location"] = location
        row["product/locationType"] = "AWS Region"
        row["product/productFamily"] = "Storage Snapshot"
        row["product/region"] = aws_region
        row["product/servicecode"] = "AmazonS3"
        row["product/sku"] = self._product_sku
        row["product/storageMedia"] = "Amazon S3"
        row["product/usagetype"] = "Requests-Tier2"
        row["pricing/publicOnDemandCost"] = str(cost)
        row["pricing/publicOnDemandRate"] = str(rate)
        row["pricing/term"] = "OnDemand"
        row["pricing/unit"] = "GB-Mo"
        self._add_tag_data(row)

        return row

    def generate_data(self, report_type=None):
        """Responsibile for generating data."""
        return self._generate_hourly_data()
