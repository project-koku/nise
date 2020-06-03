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


class DataTransferGenerator(AWSGenerator):
    """Generator for Data Transfer data."""

    DATA_TRANSFER = (
        ("{}-{}-AWS-In-Bytes", "PublicIP-In", "InterRegion Inbound"),
        ("{}-{}-AWS-Out-Bytes", "PublicIP-Out", "InterRegion Outbound"),
    )

    def __init__(self, start_date, end_date, payer_account, usage_accounts, attributes=None, tag_cols=None):
        """Initialize the data transfer generator."""
        super().__init__(start_date, end_date, payer_account, usage_accounts, attributes, tag_cols)
        self._amount = None
        self._rate = None
        self._product_sku = None
        self._resource_id = None
        self._product_code = "AmazonEC2"
        self._product_name = "Amazon Elastic Compute Cloud"
        if attributes:
            if attributes.get("product_code"):
                self._product_code = attributes.get("product_code")
            if attributes.get("product_name"):
                self._product_name = attributes.get("product_name")
            if attributes.get("resource_id"):
                self._resource_id = attributes.get("resource_id")
            if attributes.get("amount"):
                self._amount = float(attributes.get("amount"))
            if attributes.get("rate"):
                self._rate = float(attributes.get("rate"))
            if attributes.get("product_sku"):
                self._product_sku = attributes.get("product_sku")
            if attributes.get("tags"):
                self._tags = attributes.get("tags")

    def _get_data_transfer(self, rate):
        """Get data transfer info."""
        location1, aws_region, _, storage_region1 = self._get_location()
        location2, _, _, storage_region2 = self._get_location()
        trans_desc, operation, trans_type = choice(self.DATA_TRANSFER)
        trans_desc = trans_desc.format(storage_region1, storage_region2)
        description = f"${rate} per GB - {location1} data transfer to {location2}"
        return trans_desc, operation, description, location1, location2, trans_type, aws_region

    def _get_product_sku(self):
        """Generate product sku."""
        if self._product_sku:
            sku = self._product_sku
        else:
            sku = self.fake.pystr(min_chars=12, max_chars=12).upper()
        return sku

    def _update_data(self, row, start, end, **kwargs):
        """Update data with generator specific data."""
        row = self._add_common_usage_info(row, start, end)

        resource_id = self._resource_id if self._resource_id else self.fake.ean8()
        rate = self._rate if self._rate else round(uniform(0.12, 0.19), 3)
        amount = self._amount if self._amount else uniform(0.000002, 0.09)
        cost = amount * rate
        trans_desc, operation, description, location1, location2, trans_type, aws_region = self._get_data_transfer(
            rate
        )

        row["lineItem/ProductCode"] = self._product_code
        row["lineItem/UsageType"] = trans_desc
        row["lineItem/Operation"] = operation
        row["lineItem/ResourceId"] = resource_id
        row["lineItem/UsageAmount"] = str(amount)
        row["lineItem/CurrencyCode"] = "USD"
        row["lineItem/UnblendedRate"] = str(rate)
        row["lineItem/UnblendedCost"] = str(cost)
        row["lineItem/BlendedRate"] = str(rate)
        row["lineItem/BlendedCost"] = str(cost)
        row["lineItem/LineItemDescription"] = description
        row["product/ProductName"] = self._product_name
        row["product/location"] = location1
        row["product/locationType"] = "AWS Region"
        row["product/productFamily"] = "Data Transfer"
        row["product/region"] = aws_region
        row["product/servicecode"] = "AWSDataTransfer"
        row["product/sku"] = self._get_product_sku()
        row["product/toLocation"] = location2
        row["product/toLocationType"] = "AWS Region"
        row["product/transferType"] = trans_type
        row["product/usagetype"] = trans_desc
        row["pricing/publicOnDemandCost"] = str(cost)
        row["pricing/publicOnDemandRate"] = str(rate)
        row["pricing/term"] = "OnDemand"
        row["pricing/unit"] = "GB"
        self._add_tag_data(row)
        return row

    def _generate_hourly_data(self, **kwargs):
        """Create houldy data."""
        data = []
        for hour in self.hours:
            start = hour.get("start")
            end = hour.get("end")
            row = self._init_data_row(start, end)
            row = self._update_data(row, start, end)
            if self.fake.pybool():
                data.append(row)
        return data

    def generate_data(self, report_type=None):
        """Responsibile for generating data."""
        return self._generate_hourly_data()
