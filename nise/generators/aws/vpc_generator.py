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
"""Module for vpc data generation."""
from nise.generators.aws.aws_generator import AWSGenerator


class VPCGenerator(AWSGenerator):
    """Generator for VPC data."""

    def _gen_fake_data(self, count):
        """Populate TEMPLATE_KWARGS with fake values."""
        self.TEMPLATE_KWARGS["vpc_gens"] = []
        while len(self.TEMPLATE_KWARGS["vpc_gens"]) < count:
            self.TEMPLATE_KWARGS["vpc_gens"].append({"cost": 0.05, "rate": 0.05})

    def _update_data(self, row, start, end, **kwargs):
        """Update data with generator specific data."""
        current_config = kwargs.get("config", {})

        cost = current_config.get("cost")
        rate = current_config.get("rate")

        location, aws_region, avail_zone, _ = self._get_location(config=current_config)
        row = self._add_common_usage_info(row, start, end)
        region_short_code = self._generate_region_short_code(aws_region)
        usage_type = f"{region_short_code}-VPN-Usage-Hours:ipsec.1"

        row["lineItem/ProductCode"] = "AmazonVPC"
        row["lineItem/UsageType"] = usage_type
        row["lineItem/Operation"] = "CreateVpnConnection"
        row["lineItem/AvailabilityZone"] = avail_zone
        row["lineItem/ResourceId"] = current_config.get("resource_id")
        row["lineItem/UsageAmount"] = "1"
        row["lineItem/CurrencyCode"] = "USD"
        row["lineItem/UnblendedRate"] = rate
        row["lineItem/UnblendedCost"] = cost
        row["lineItem/BlendedRate"] = rate
        row["lineItem/BlendedCost"] = cost
        row["lineItem/LineItemDescription"] = "$0.05 per VPN Connection-Hour"
        row["product/ProductName"] = "Amazon Virtual Private Cloud"
        row["product/clockSpeed"] = ""
        row["product/currentGeneration"] = ""
        row["product/ecu"] = ""
        row["product/enhancedNetworkingSupported"] = ""
        row["product/instanceFamily"] = ""
        row["product/instanceType"] = ""
        row["product/licenseModel"] = ""
        row["product/location"] = location
        row["product/locationType"] = "AWS Region"
        row["product/memory"] = ""
        row["product/networkPerformance"] = ""
        row["product/operatingSystem"] = ""
        row["product/operation"] = "CreateVpnConnection"
        row["product/physicalProcessor"] = ""
        row["product/preInstalledSw"] = ""
        row["product/processorArchitecture"] = ""
        row["product/processorFeatures"] = ""
        row["product/productFamily"] = "Cloud Connectivity"
        row["product/region"] = aws_region
        row["product/servicecode"] = "AmazonVPC"
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
