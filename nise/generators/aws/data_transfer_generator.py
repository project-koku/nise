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
        # (usage type, operation, transfer type)
        ("{region1}-{region2}-AWS-{direction}-Bytes", "PublicIP-{direction}", "InterRegion {direction}bound"),
        ("DataTransfer-{direction}-Bytes", "RunInstances", ""),
        ("{region1}-DataTransfer-Regional-Bytes", "PublicIP-{direction}", ""),
        ("{region1}-DataTransfer-Regional-Bytes", "InterZone-{direction}", ""),
    )
    DATA_TRANSFER_DIRECTIONS = ("in", "out")

    def __init__(self, start_date, end_date, currency, payer_account, usage_accounts, attributes=None, tag_cols=None):
        """Initialize the data transfer generator."""
        super().__init__(start_date, end_date, currency, payer_account, usage_accounts, attributes, tag_cols)

        self._amount = float(self.attributes.get("amount", 0)) or None
        self._data_direction = self.attributes.get("data_direction")
        self._product_code = self.attributes.get("product_code", "AmazonEC2")
        self._product_name = self.attributes.get("product_name", "Amazon Elastic Compute Cloud")
        self._product_sku = self.attributes.get("product_sku")
        self._rate = float(self.attributes.get("rate", 0)) or None
        self._resource_id = f"i-{self.attributes.get('resource_id', self.fake.ean8())}"
        self._saving = float(self.attributes.get("saving", 0)) or None
        self._negation = self.attributes.get("negation") or False
        self._tags = self.attributes.get("tags", self._tags)

    @property
    def data_direction(self):
        if self._data_direction is not None:
            return self._data_direction.capitalize()

        # Purposefully not caching this value so a different value is returned on each call
        return choice(self.DATA_TRANSFER_DIRECTIONS).capitalize()

    def _get_data_transfer(self, rate):
        """Get data transfer info."""
        location1, aws_region, _, storage_region1 = self._get_location()
        location2, _, _, storage_region2 = self._get_location()
        trans_desc, operation, trans_type = choice(self.DATA_TRANSFER)
        trans_desc = trans_desc.format(region1=storage_region1, region2=storage_region2, direction=self.data_direction)
        operation = operation.format(direction=self.data_direction)
        trans_type = trans_type.format(direction=self.data_direction)
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
        saving = self._saving
        negation = self._negation
        amount = self._amount if self._amount else uniform(0.000002, 0.09)
        cost = amount * rate
        trans_desc, operation, description, location1, location2, trans_type, aws_region = self._get_data_transfer(rate)

        row["lineItem/ProductCode"] = self._product_code
        row["lineItem/UsageType"] = trans_desc
        row["lineItem/Operation"] = operation
        row["lineItem/ResourceId"] = resource_id
        row["lineItem/UsageAmount"] = str(amount)
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
        row["savingsPlan/SavingsPlanEffectiveCost"] = str(saving)
        row["savingsPlan/SavingsPlanRate"] = str(saving)

        # Overwrite lineItem/LineItemType for items with applied Savings plan
        if saving is not None:
            row["lineItem/LineItemType"] = "SavingsPlanCoveredUsage"

        if negation:
            row["lineItem/LineItemType"] = "SavingsPlanNegation"
            row["lineItem/UnblendedCost"] = -abs(cost)
            row["lineItem/UnblendedRate"] = -abs(rate)
            row["lineItem/BlendedCost"] = -abs(cost)
            row["lineItem/BlendedRate"] = -abs(rate)
            row["lineItem/LineItemDescription"] = (
                f"SavingsPlanNegation used by AccountId : {self.payer_account} and UsageSku : {self._product_sku}"
            )
            row["lineItem/ResourceId"] = None
            row["savingsPlan/SavingsPlanEffectiveCost"] = None
            row["savingsPlan/SavingsPlanRate"] = None
        else:
            self._add_tag_data(row)
            self._add_category_data(row)
        return row

    def generate_data(self, report_type=None):
        """Responsibile for generating data."""
        return self._generate_hourly_data()
