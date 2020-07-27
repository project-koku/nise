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
"""Module for ec2 data generation."""
from random import choice

from nise.generators.aws.aws_generator import AWSGenerator
from nise.generators.aws.constants import ARCHS
from nise.generators.aws.constants import EC2_INSTANCE_TYPES
from nise.generators.aws.constants import REGIONS


class EC2Generator(AWSGenerator):
    """Generator for EC2 data."""

    def _gen_fake_data(self, count):
        """Populate TEMPLATE_KWARGS with fake values.

        The base template has defaults for most values. The values set here have extra requirements.
        """
        self.TEMPLATE_KWARGS["ec2_gens"] = []
        while len(self.TEMPLATE_KWARGS["ec2_gens"]) < count:
            self.TEMPLATE_KWARGS["ec2_gens"].append(
                {
                    "region": choice(REGIONS)[1],
                    "processor_arch": choice(ARCHS),
                    "instance_type": choice(EC2_INSTANCE_TYPES),
                    "tags": [{"key": self.fake.word(), "value": self.fake.word()}],
                }
            )

    def _update_data(self, row, start, end, **kwargs):
        """Update data with generator specific data."""
        current_config = kwargs.get("config", {})

        inst_type = current_config.get("instance_type", {}).get("inst_type")
        cost = current_config.get("instance_type", {}).get("cost")
        rate = current_config.get("instance_type", {}).get("rate")

        location, aws_region, avail_zone, _ = self._get_location(config=current_config)
        row = self._add_common_usage_info(row, start, end)

        row["lineItem/ProductCode"] = "AmazonEC2"
        row["lineItem/UsageType"] = f"BoxUsage:{inst_type}"
        row["lineItem/Operation"] = "RunInstances"
        row["lineItem/AvailabilityZone"] = avail_zone
        row["lineItem/ResourceId"] = current_config.get("resource_id")
        row["lineItem/UsageAmount"] = "1"
        row["lineItem/CurrencyCode"] = "USD"
        row["lineItem/UnblendedRate"] = rate
        row["lineItem/UnblendedCost"] = cost
        row["lineItem/BlendedRate"] = rate
        row["lineItem/BlendedCost"] = cost
        row["lineItem/LineItemDescription"] = (
            current_config.get("instance_type", {}).get("desc").format(cost, inst_type)
        )
        row["product/ProductName"] = "Amazon Elastic Compute Cloud"
        row["product/clockSpeed"] = "2.8 GHz"
        row["product/currentGeneration"] = "Yes"
        row["product/ecu"] = "14"
        row["product/enhancedNetworkingSupported"] = "Yes"
        row["product/instanceFamily"] = current_config.get("instance_type", {}).get("family")
        row["product/instanceType"] = inst_type
        row["product/licenseModel"] = "No License required"
        row["product/location"] = location
        row["product/locationType"] = "AWS Region"
        row["product/memory"] = current_config.get("instance_type", {}).get("memory")
        row["product/networkPerformance"] = "Moderate"
        row["product/operatingSystem"] = "Linux"
        row["product/operation"] = "RunInstances"
        row["product/physicalProcessor"] = "Intel Xeon Family"
        row["product/preInstalledSw"] = "NA"
        row["product/processorArchitecture"] = current_config.get("processor_arch")
        row["product/processorFeatures"] = "Intel AVX Intel Turbo"
        row["product/productFamily"] = "Compute Instance"
        row["product/region"] = aws_region
        row["product/servicecode"] = "AmazonEC2"
        row["product/sku"] = current_config.get("product_sku")
        row["product/storage"] = current_config.get("instance_type", {}).get("storage")
        row["product/tenancy"] = "Shared"
        row["product/usagetype"] = f"BoxUsage:{inst_type}"
        row["product/vcpu"] = current_config.get("instance_type", {}).get("vcpu")
        row["pricing/publicOnDemandCost"] = cost
        row["pricing/publicOnDemandRate"] = rate
        row["pricing/term"] = "OnDemand"
        row["pricing/unit"] = "Hrs"
        self._add_tag_data(row)

        return row

    def generate_data(self, report_type=None):
        """Responsibile for generating data."""
        return self._generate_hourly_data()
