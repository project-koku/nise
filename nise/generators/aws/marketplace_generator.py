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
import string
from random import choice
from random import uniform

from nise.generators.aws.aws_generator import AWSGenerator


class MarketplaceGenerator(AWSGenerator):
    """Defines a generator for AWS Marketplace"""

    LEGAL_ENTITY_CHOICES = ("Red Hat", "Red Hat Inc.", "Amazon Web Services, Inc.")

    MARKETPLACE_PRODUCTS = (
        "Red Hat OpenShift Service on AWS",
        "Red Hat Enterprise Linux 7",
        "Red Hat Enterprise Linux 8",
    )

    def __init__(self, start_date, end_date, currency, payer_account, usage_accounts, attributes={}, tag_cols=None):
        """Initialize the generator."""
        super().__init__(start_date, end_date, currency, payer_account, usage_accounts, attributes, tag_cols)

        self._legal_entity = choice(self.LEGAL_ENTITY_CHOICES)
        self._amount = uniform(0.2, 300.99)
        self._rate = round(uniform(0.02, 0.16), 3)
        self._resource_id = "i-{}".format(self.fake.ean8())
        self._product_sku = self.fake.pystr(min_chars=12, max_chars=12).upper()

        for attribute in self.attributes:
            setattr(self, f"_{attribute}", self.attributes.get(attribute))

        if tag_cols:
            self.RESOURCE_TAG_COLS.update(tag_cols)
            self.AWS_COLUMNS.update(tag_cols)

    @property
    def rate_code(self):
        """Return a formatted rate code."""
        if hasattr(self, "_rate_code"):
            return self._rate_code

        chars = string.ascii_uppercase + string.digits

        return (
            "".join([choice(chars) for _ in range(16)])
            + "."
            + "".join([choice(chars) for _ in range(10)])
            + "."
            + "".join([choice(chars) for _ in range(10)])
        )

    @property
    def rate_id(self):
        """Return a formatted rate code."""
        if hasattr(self, "_rate_id"):
            return self._rate_id
        return "".join([choice(string.digits) for _ in range(10)])

    @property
    def subscription_id(self):
        """Return a formatted rate code."""
        if hasattr(self, "_subscription_id"):
            return self._subscription_id
        return "".join([choice(string.digits) for _ in range(10)])

    def _update_data(self, row, start, end, **kwargs):
        """Update data with generator specific data."""
        self.AWS_COLUMNS.update(self.AWS_COLUMNS)
        row = self._add_common_usage_info(row, start, end)

        cost = self._amount * self._rate
        _, aws_region, avail_zone, _ = self._get_location()
        description = "AWS Marketplace hourly software usage|us-east-1|m5.xlarge"
        amazon_resource_name = f"arn:aws:ec2:{avail_zone}:{self.payer_account}:instance/i-{self._resource_id}"

        row["bill/BillingEntity"] = "AWS Marketplace"

        row["lineItem/UsageAccountId"] = choice(self.usage_accounts)
        row["lineItem/LegalEntity"] = self._legal_entity
        row["lineItem/LineItemType"] = "Usage"
        row["lineItem/UsageStartDate"] = start
        row["lineItem/UsageEndDate"] = end
        row["lineItem/ProductCode"] = "5hnnev4d0v7mapf09j0v8of0o2"
        row["lineItem/UsageType"] = "SoftwareUsage:m5.xlarge"
        row["lineItem/Operation"] = "Hourly"
        row["lineItem/AvailabilityZone"] = avail_zone
        row["lineItem/ResourceId"] = amazon_resource_name
        row["lineItem/UsageAmount"] = self._amount
        row["lineItem/CurrencyCode"] = self.currency
        row["lineItem/UnblendedRate"] = self._rate
        row["lineItem/UnblendedCost"] = cost
        row["lineItem/BlendedRate"] = self._rate
        row["lineItem/BlendedCost"] = cost
        row["lineItem/LineItemDescription"] = description

        row["product/ProductName"] = choice(self.MARKETPLACE_PRODUCTS)
        row["product/region"] = aws_region
        row["product/sku"] = self._product_sku

        row["pricing/publicOnDemandCost"] = cost
        row["pricing/unit"] = "Hrs"
        row["pricing/RateCode"] = self.rate_code
        row["pricing/RateId"] = self.rate_id
        row["pricing/currency"] = self.currency
        row["pricing/term"] = "OnDemand"

        row["reservation/SubscriptionId"] = self.subscription_id

        self._add_tag_data(row)

        return row

    def generate_data(self, report_type=None):
        """Responsibile for generating data."""
        return self._generate_hourly_data()
