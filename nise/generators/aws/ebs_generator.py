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
from random import choice
from random import uniform

from nise.generators.aws.aws_generator import AWSGenerator


class EBSGenerator(AWSGenerator):
    """Generator for EBS data."""

    STORAGE = (
        ("Hundreds", "40 - 200", "40 - 90 MB/sec", "1 TiB", "HDD-backed", "Magnetic"),
        ("3000 for volumes <= 1 TiB", "10000", "160 MB/sec", "16 TiB", "SSD-backed", "General Purpose"),
    )

    def __init__(self, start_date, end_date, payer_account, usage_accounts, attributes=None):
        """Initialize the EBS generator."""
        super().__init__(start_date, end_date, payer_account, usage_accounts, attributes)
        self._resource_id = "vol-{}".format(self.fake.ean8())
        self._amount = uniform(0.2, 300.99)
        self._rate = round(uniform(0.02, 0.16), 3)
        self._product_sku = self.fake.pystr(min_chars=12, max_chars=12).upper()

        if self.attributes:
            if self.attributes.get("resource_id"):
                self._resource_id = "vol-{}".format(self.attributes.get("resource_id"))
            if self.attributes.get("amount"):
                self._amount = self.attributes.get("amount")
            if self.attributes.get("rate"):
                self._rate = self.attributes.get("rate")
            if self.attributes.get("product_sku"):
                self._product_sku = self.attributes.get("product_sku")
            if self.attributes.get("tags"):
                self._tags = self.attributes.get("tags")

    def _get_storage(self):
        """Get storage data."""
        return choice(self.STORAGE)

    def _update_data(self, row, start, end, **kwargs):
        """Update data with generator specific data."""
        row = self._add_common_usage_info(row, start, end)

        rate = self._rate
        amount = self._amount
        cost = amount * rate
        location, aws_region, _, storage_region = self._get_location()
        description = f"${rate} per GB-Month of snapshot data stored - {location}"
        burst, max_iops, max_thru, max_vol_size, vol_backed, vol_type = self._get_storage()

        row["lineItem/ProductCode"] = "AmazonEC2"
        row["lineItem/UsageType"] = f"{storage_region}:VolumeUsage"
        row["lineItem/Operation"] = "CreateVolume"
        row["lineItem/ResourceId"] = self._resource_id
        row["lineItem/UsageAmount"] = str(amount)
        row["lineItem/CurrencyCode"] = "USD"
        row["lineItem/UnblendedRate"] = str(rate)
        row["lineItem/UnblendedCost"] = str(cost)
        row["lineItem/BlendedRate"] = str(rate)
        row["lineItem/BlendedCost"] = str(cost)
        row["lineItem/LineItemDescription"] = description
        row["product/ProductName"] = "Amazon Elastic Compute Cloud"
        row["product/location"] = location
        row["product/locationType"] = "AWS Region"
        row["product/maxIopsBurstPerformance"] = burst
        row["product/maxIopsvolume"] = max_iops
        row["product/maxThroughputvolume"] = max_thru
        row["product/maxVolumeSize"] = max_vol_size
        row["product/productFamily"] = "Storage"
        row["product/region"] = aws_region
        row["product/servicecode"] = "AmazonEC2"
        row["product/sku"] = self._product_sku
        row["product/storageMedia"] = vol_backed
        row["product/usagetype"] = f"{storage_region}:VolumeUsage"
        row["product/volumeType"] = vol_type
        row["pricing/publicOnDemandCost"] = str(cost)
        row["pricing/publicOnDemandRate"] = str(rate)
        row["pricing/term"] = "OnDemand"
        row["pricing/unit"] = "GB-Mo"
        self._add_tag_data(row)

        return row

    def generate_data(self, report_type=None):
        """Responsibile for generating data."""
        return self._generate_hourly_data()
