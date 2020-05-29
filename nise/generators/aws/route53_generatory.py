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
"""Module for route 53 data generation."""
from random import choices

from nise.generators.aws.aws_generator import AWSGenerator

ROUTE_53_PRODUCTS_DICT = {
    "DNS Zone": ("DNS Zone", "HostedZone", 0.500000000, 0.500000000),
    "DNS Query": ("DNS Query", "DNS-Queries", 0.000000400, 0.000000400),
}
ROUTE_53_PRODUCTS = list(ROUTE_53_PRODUCTS_DICT.values())


class Route53Generator(AWSGenerator):
    """Generator for Route53 data."""

    def __init__(self, start_date, end_date, payer_account, usage_accounts, attributes=None):
        """Initialize the Route53 generator."""
        super().__init__(start_date, end_date, payer_account, usage_accounts, attributes)
        self._product_sku = self.fake.pystr(min_chars=12, max_chars=12).upper()
        self._product_family = None
        if self.attributes:
            if self.attributes.get("product_family"):
                self._product_family = self.attributes.get("product_family")
            if self.attributes.get("product_sku"):
                self._product_sku = self.attributes.get("product_sku")
            if self.attributes.get("tags"):
                self._tags = self.attributes.get("tags")

    def _get_arn(self):
        """Create an amazon resource name."""
        return "arn:aws:Route53:::hostedzone:{}".format(self.fake.ean8())

    def _update_data(self, row, start, end, **kwargs):
        """Update data with generator specific data."""
        if self._product_family:
            product_family, usage_type, rate, cost = ROUTE_53_PRODUCTS_DICT.get(self._product_family)
        else:
            product_family, usage_type, rate, cost = choices(ROUTE_53_PRODUCTS, weights=[1, 10])[0]
        operation = self.fake.pystr(min_chars=1, max_chars=6).upper()
        if usage_type == "HostedZone":
            operation = usage_type
        row = self._add_common_usage_info(row, start, end)

        row["lineItem/ProductCode"] = "AmazonRoute53"
        row["lineItem/UsageType"] = usage_type
        row["lineItem/Operation"] = operation
        row["lineItem/AvailabilityZone"] = ""
        row["lineItem/ResourceId"] = self._get_arn()
        row["lineItem/UsageAmount"] = "1"
        row["lineItem/CurrencyCode"] = "USD"
        row["lineItem/UnblendedRate"] = rate
        row["lineItem/UnblendedCost"] = cost
        row["lineItem/BlendedRate"] = rate
        row["lineItem/BlendedCost"] = cost
        row["lineItem/LineItemDescription"] = ""
        row["product/ProductName"] = "Amazon Route 53"
        row["product/clockSpeed"] = ""
        row["product/currentGeneration"] = ""
        row["product/ecu"] = ""
        row["product/enhancedNetworkingSupported"] = ""
        row["product/instanceFamily"] = ""
        row["product/instanceType"] = ""
        row["product/licenseModel"] = ""
        row["product/location"] = ""
        row["product/locationType"] = "AWS Region"
        row["product/memory"] = ""
        row["product/networkPerformance"] = ""
        row["product/operatingSystem"] = ""
        row["product/operation"] = operation
        row["product/physicalProcessor"] = ""
        row["product/preInstalledSw"] = ""
        row["product/processorArchitecture"] = ""
        row["product/processorFeatures"] = ""
        row["product/productFamily"] = product_family
        row["product/region"] = "global"
        row["product/servicecode"] = "AmazonRoute53"
        row["product/sku"] = self._product_sku
        row["product/storage"] = ""
        row["product/tenancy"] = ""
        row["product/usagetype"] = usage_type
        row["product/vcpu"] = ""
        row["pricing/publicOnDemandCost"] = cost
        row["pricing/publicOnDemandRate"] = rate
        row["pricing/term"] = "OnDemand"
        row["pricing/unit"] = "Hrs"
        self._add_tag_data(row)

        return row

    def generate_data(self, report_type=None):
        """Responsibile for generating data."""
        return self._generate_hourly_data()
