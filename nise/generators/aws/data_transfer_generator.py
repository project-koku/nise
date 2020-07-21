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
from nise.generators.aws.constants import REGIONS


class DataTransferGenerator(AWSGenerator):
    """Generator for Data Transfer data."""

    DATA_TRANSFER = (
        ("{}-{}-AWS-In-Bytes", "PublicIP-In", "InterRegion Inbound"),
        ("{}-{}-AWS-Out-Bytes", "PublicIP-Out", "InterRegion Outbound"),
    )

    def _gen_fake_data(self, count):
        """Populate TEMPLATE_KWARGS with fake values.

        The base template has defaults for most values. The values set here have extra requirements.
        """
        self.TEMPLATE_KWARGS["data_transfer_gens"] = []
        while len(self.TEMPLATE_KWARGS["data_transfer_gens"]) < count:
            self.TEMPLATE_KWARGS["data_transfer_gens"].append(
                {
                    "amount": uniform(0.000002, 0.09),
                    "rate": round(uniform(0.12, 0.19), 3),
                    "region": choice(REGIONS)[1],
                }
            )

    def _get_data_transfer(self, rate, config={}):
        """Get data transfer info."""
        location1, aws_region, _, storage_region1 = self._get_location(config=config)
        location2, _, _, storage_region2 = self._get_location(config=config)
        trans_desc, operation, trans_type = choice(self.DATA_TRANSFER)
        trans_desc = trans_desc.format(storage_region1, storage_region2)
        description = f"${rate} per GB - {location1} data transfer to {location2}"
        return trans_desc, operation, description, location1, location2, trans_type, aws_region

    def _update_data(self, row, start, end, **kwargs):
        """Update data with generator specific data."""
        current_config = kwargs.get("config", {})

        row = self._add_common_usage_info(row, start, end)

        rate = current_config.get("rate")
        amount = current_config.get("amount")
        cost = amount * rate
        trans_desc, operation, description, location1, location2, trans_type, aws_region = self._get_data_transfer(
            rate, config=current_config
        )

        row["lineItem/ProductCode"] = current_config.get("product_code")
        row["lineItem/UsageType"] = trans_desc
        row["lineItem/Operation"] = operation
        row["lineItem/ResourceId"] = current_config.get("resource_id")
        row["lineItem/UsageAmount"] = str(amount)
        row["lineItem/CurrencyCode"] = "USD"
        row["lineItem/UnblendedRate"] = str(rate)
        row["lineItem/UnblendedCost"] = str(cost)
        row["lineItem/BlendedRate"] = str(rate)
        row["lineItem/BlendedCost"] = str(cost)
        row["lineItem/LineItemDescription"] = description
        row["product/ProductName"] = current_config.get("product_name")
        row["product/location"] = location1
        row["product/locationType"] = "AWS Region"
        row["product/productFamily"] = "Data Transfer"
        row["product/region"] = aws_region
        row["product/servicecode"] = "AWSDataTransfer"
        row["product/sku"] = current_config.get("product_sku")
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
        """Create hourly data."""
        data = []
        for hour in self.hours:
            for cfg in self.config:
                start = hour.get("start")
                end = hour.get("end")
                row = self._init_data_row(start, end, config=cfg)
                row = self._update_data(row, start, end, config=cfg)
                data.append(row)
        return data

    def generate_data(self, report_type=None):
        """Responsibile for generating data."""
        return self._generate_hourly_data()
