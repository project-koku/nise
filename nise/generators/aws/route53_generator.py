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
from nise.generators.aws.constants import ROUTE_53_PRODUCTS
from nise.generators.aws.constants import ROUTE_53_PRODUCTS_DICT


class Route53Generator(AWSGenerator):
    """Generator for Route53 data."""

    def _gen_fake_data(self, count):
        """Populate TEMPLATE_KWARGS with fake values."""
        self.TEMPLATE_KWARGS["route53_gens"] = []
        while len(self.TEMPLATE_KWARGS["route53_gens"]) < count:
            self.TEMPLATE_KWARGS["route53_gens"].append(
                {"product_family": choices(ROUTE_53_PRODUCTS, weights=[1, 10])[0]}
            )

    def _get_arn(self, resource_id):
        """Create an amazon resource name."""
        return f"arn:aws:Route53:::hostedzone:{resource_id}"

    def _update_data(self, row, start, end, **kwargs):
        """Update data with generator specific data."""
        current_config = kwargs.get("config", {})

        product_family, usage_type, rate, cost = ROUTE_53_PRODUCTS_DICT.get(current_config.get("product_family"))
        operation = self.fake.pystr(min_chars=1, max_chars=6).upper()
        if usage_type == "HostedZone":
            operation = usage_type
        row = self._add_common_usage_info(row, start, end)

        row["lineItem/ProductCode"] = "AmazonRoute53"
        row["lineItem/UsageType"] = usage_type
        row["lineItem/Operation"] = operation
        row["lineItem/AvailabilityZone"] = ""
        row["lineItem/ResourceId"] = self._get_arn(current_config.get("resource_id"))
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
        row["product/sku"] = current_config.get("product_sku")
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
