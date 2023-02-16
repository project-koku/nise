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

    def __init__(self, start_date, end_date, currency, payer_account, usage_accounts, attributes=None, tag_cols=None):
        """Initialize the VPC generator."""
        super().__init__(start_date, end_date, currency, payer_account, usage_accounts, attributes, tag_cols)
        self._resource_id = "vpn-{}".format(self.fake.ean8())
        self._product_sku = self.fake.pystr(min_chars=12, max_chars=12).upper()
        self._rate = None
        self._cost = None
        if self.attributes:
            if self.attributes.get("resource_id"):
                self._resource_id = "vpn-{}".format(self.attributes.get("resource_id"))
            if self.attributes.get("product_sku"):
                self._product_sku = self.attributes.get("product_sku")
            if self.attributes.get("tags"):
                self._tags = self.attributes.get("tags")
            if self.attributes.get("cost"):
                self._cost = self.attributes.get("cost")
            if self.attributes.get("rate"):
                self._rate = self.attributes.get("rate")

    def _update_data(self, row, start, end, **kwargs):
        """Update data with generator specific data."""
        default_cost = 0.05
        default_rate = 0.05
        rate = float(self._rate) if self._rate else default_rate
        cost = float(self._cost) if self._cost else default_cost
        location, aws_region, avail_zone, _ = self._get_location()
        row = self._add_common_usage_info(row, start, end)
        region_short_code = self._generate_region_short_code(aws_region)
        usage_type = f"{region_short_code}-VPN-Usage-Hours:ipsec.1"

        row["lineItem/ProductCode"] = "AmazonVPC"
        row["lineItem/UsageType"] = usage_type
        row["lineItem/Operation"] = "CreateVpnConnection"
        row["lineItem/AvailabilityZone"] = avail_zone
        row["lineItem/ResourceId"] = self._resource_id
        row["lineItem/UsageAmount"] = "1"
        row["lineItem/UnblendedRate"] = rate
        row["lineItem/UnblendedCost"] = cost
        row["lineItem/BlendedRate"] = rate
        row["lineItem/BlendedCost"] = cost
        row["lineItem/LineItemDescription"] = f"${self._rate} per VPN Connection-Hour"
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
        self._add_category_data(row)

        return row

    def generate_data(self, report_type=None):
        """Responsibile for generating data."""
        return self._generate_hourly_data()
