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
"""Module for marketplace data generation."""
from random import uniform

from nise.generators.aws.aws_generator import AWSGenerator


class MarketplaceGenerator(AWSGenerator):
    """Generator for Marketplace data."""

    def __init__(self, start_date, end_date, payer_account, usage_accounts, attributes=None, tag_cols=None):
        """Initialize the Marketplace generator."""
        super().__init__(start_date, end_date, payer_account, usage_accounts, attributes, tag_cols)
        self._amount = uniform(0.2, 6000.99)
        self._rate = round(uniform(0.02, 0.06), 3)
        self._product_sku = self.fake.pystr(min_chars=12, max_chars=12).upper()
        self._resource_id = self.fake.ean8()

        # add AWS Marketplace specific columns
        aws_marketplace_cols = {
            "lineItem/LegalEntity",
            "pricing/currency",
            "pricing/RateCode",
            "pricing/RateId",
            "reservation/SubscriptionId",
            "resourceTags/aws:createdBy",
        }

        self.AWS_COLUMNS.update(aws_marketplace_cols)

        if self.attributes:
            if self.attributes.get("amount"):
                self._amount = float(self.attributes.get("amount"))
            if self.attributes.get("rate"):
                self._rate = float(self.attributes.get("rate"))
            if self.attributes.get("product_sku"):
                self._product_sku = self.attributes.get("product_sku")
            if self.attributes.get("resource_id"):
                self._resource_id = self.attributes.get("resource_id")
            if self.attributes.get("tags"):
                self._tags = self.attributes.get("tags")

    def _get_arn(self, avail_zone):
        """Create an amazon resource name."""
        return f"arn:aws:ec2:{avail_zone}:{self.payer_account}:instance/i-{self._resource_id}"

    def _update_data(self, row, start, end, **kwargs):
        """Update data with generator specific data."""
        row = self._add_common_usage_info(row, start, end)

        rate = self._rate
        amount = self._amount
        cost = amount * rate
        location, aws_region, avail_zone, _ = self._get_location()
        description = "AWS Marketplace hourly software usage|us-east-1|m5.xlarge"
        amazon_resource_name = self._get_arn(avail_zone)

        row["identity/LineItemId"] = "diygn5vanaqsvysz3prxwrekztiipfu7zywyauupnpmpi4fmd5dq"
        row["identity/TimeInterval"] = "2021-11-23T17:49:15Z/2021-12-01T00:00:00Z"

        row["bill/InvoiceId"] = "2021-11-23T17:49:15Z/2021-12-01T00:00:00Z"
        row["bill/BillingEntity"] = "AWS Marketplace"
        row["bill/BillType"] = "Anniversary"
        row["bill/PayerAccountId"] = "589173575009"
        row["bill/BillingPeriodStartDate"] = "2021-11-01T00:00:00Z"
        row["bill/BillingPeriodEndDate"] = "2021-12-01T00:00:00Z"

        row["lineItem/ProductCode"] = "5hnnev4d0v7mapf09j0v8of0o2"
        row["lineItem/UsageType"] = "SoftwareUsage:m5.xlarge"
        row["lineItem/Operation"] = "Hourly"
        row["lineItem/AvailabilityZone"] = avail_zone
        row["lineItem/ResourceId"] = amazon_resource_name
        row["lineItem/UsageAmount"] = "1"
        row["lineItem/CurrencyCode"] = "USD"
        row["lineItem/UnblendedRate"] = str(rate)
        row["lineItem/UnblendedCost"] = str(cost)
        row["lineItem/BlendedRate"] = str(rate)
        row["lineItem/BlendedCost"] = str(cost)
        row["lineItem/LineItemDescription"] = description

        row["product/ProductName"] = "Red Hat OpenShift Service on AWS"
        row["product/region"] = aws_region
        row["product/sku"] = self._product_sku

        row["pricing/publicOnDemandCost"] = cost
        row["pricing/unit"] = "Hrs"
        row["pricing/RateCode"] = "VDHYUHU8G2Z5AZY3.4799GE89SK.6YS6EN2CT7"
        row["pricing/RateId"] = "4981658079"
        row["pricing/currency"] = "USD"
        row["pricing/term"] = "OnDemand"

        row["reservation/SubscriptionId"] = "7592738291"

        row["resourceTags/aws:createdBy"] = "AssumedRole:AROAYSLL3JVQ6DYUNKWQJ:1637692740557658269"

        self._add_tag_data(row)

        return row

    def generate_data(self, report_type=None):
        """Responsibile for generating data."""
        return self._generate_hourly_data()
