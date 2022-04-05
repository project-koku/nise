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
"""Module for rds data generation."""
from random import choice

from nise.generators.aws.aws_generator import AWSGenerator


class RDSGenerator(AWSGenerator):
    """Generator for RDS data."""

    INSTANCE_TYPES = (
        (
            "db.t3.medium",
            "2",
            "4 GiB",
            "EBS-Only",
            "Memory Optimized",
            "0.072",
            "0.072",
            "${} per On Demand Linux {} Instance Hour",
        ),
        (
            "db.t3.large",
            "2",
            "8 GiB",
            "EBS Only",
            "General Purpose",
            "0.145",
            "0.145",
            "${} per On Demand Linux {} Instance Hour",
        ),
        (
            "db.m5.xlarge",
            "4",
            "16 GiB",
            "1 x 200 NVMe SSD",
            "Compute Optimized",
            "0.356",
            "0.356",
            "${} per On Demand Linux {} Instance Hour",
        ),
        (
            "db.r5.2xlarge",
            "8",
            "64 GiB",
            "EBS-Only",
            "Compute Optimized",
            "1.00",
            "1.00",
            "${} per On Demand Linux {} Instance Hour",
        ),
    )

    ARCHS = ("32-bit", "64-bit")

    def __init__(self, start_date, end_date, currency, payer_account, usage_accounts, attributes=None, tag_cols=None):
        """Initialize the RDS generator."""
        super().__init__(start_date, end_date, currency, payer_account, usage_accounts, attributes, tag_cols)
        self._processor_arch = choice(self.ARCHS)
        self._product_sku = self.fake.pystr(min_chars=12, max_chars=12).upper()
        self._instance_type = choice(self.INSTANCE_TYPES)
        self._resource_id = "i-{}".format(self.fake.ean8())
        if self.attributes:
            if self.attributes.get("product_sku"):
                self._product_sku = self.attributes.get("product_sku")
            if self.attributes.get("resource_id"):
                self._resource_id = "i-{}".format(self.attributes.get("resource_id"))
            if self.attributes.get("tags"):
                self._tags = self.attributes.get("tags")
            instance_type = self.attributes.get("instance_type")
            if instance_type:
                self._instance_type = (
                    instance_type.get("inst_type"),
                    instance_type.get("vcpu"),
                    instance_type.get("memory"),
                    instance_type.get("storage"),
                    instance_type.get("family"),
                    instance_type.get("cost"),
                    instance_type.get("rate"),
                    "${} per On Demand Linux {} Instance Hour",
                )

    def _get_arn(self, avail_zone):
        """Create an amazon resource name."""
        return f"arn:aws:rds:{avail_zone}:{self.payer_account}:db:{self._resource_id}"

    def _update_data(self, row, start, end, **kwargs):
        """Update data with generator specific data."""
        inst_type, vcpu, memory, storage, family, cost, rate, description = self._instance_type
        inst_description = description.format(cost, inst_type)
        location, aws_region, avail_zone, _ = self._get_location()
        row = self._add_common_usage_info(row, start, end)
        # split_region = aws_region.split('-')
        # region_short_code = aws_region[0:2].upper() + split_region[1][0].upper() + split_region[2]
        region_short_code = self._generate_region_short_code(aws_region)

        row["lineItem/ProductCode"] = "AmazonRDS"
        row["lineItem/UsageType"] = f"{region_short_code}-InstanceUsage:{inst_type}"
        row["lineItem/Operation"] = "CreateDBInstance"
        row["lineItem/AvailabilityZone"] = avail_zone
        row["lineItem/ResourceId"] = self._get_arn(avail_zone)
        row["lineItem/UsageAmount"] = "1"
        row["lineItem/UnblendedRate"] = rate
        row["lineItem/UnblendedCost"] = cost
        row["lineItem/BlendedRate"] = rate
        row["lineItem/BlendedCost"] = cost
        row["lineItem/LineItemDescription"] = inst_description
        row["product/ProductName"] = "Amazon Relational Database Service"
        row["product/clockSpeed"] = "2.8 GHz"
        row["product/currentGeneration"] = "Yes"
        row["product/ecu"] = "14"
        row["product/enhancedNetworkingSupported"] = "Yes"
        row["product/instanceFamily"] = family
        row["product/instanceType"] = inst_type
        row["product/licenseModel"] = "No License required"
        row["product/location"] = location
        row["product/locationType"] = "AWS Region"
        row["product/memory"] = memory
        row["product/networkPerformance"] = "Moderate"
        row["product/operatingSystem"] = "Linux"
        row["product/operation"] = "RunInstances"
        row["product/physicalProcessor"] = "Intel Xeon Family"
        row["product/preInstalledSw"] = "NA"
        row["product/processorArchitecture"] = self._processor_arch
        row["product/processorFeatures"] = "Intel AVX Intel Turbo"
        row["product/productFamily"] = "Database Instance"
        row["product/region"] = aws_region
        row["product/servicecode"] = "AmazonRDS"
        row["product/sku"] = self._product_sku
        row["product/storage"] = storage
        row["product/tenancy"] = "Shared"
        row["product/usagetype"] = f"BoxUsage:{inst_type}"
        row["product/vcpu"] = vcpu
        row["pricing/publicOnDemandCost"] = cost
        row["pricing/publicOnDemandRate"] = rate
        row["pricing/term"] = "OnDemand"
        row["pricing/unit"] = "Hrs"
        self._add_tag_data(row)

        return row

    def generate_data(self, report_type=None):
        """Responsibile for generating data."""
        return self._generate_hourly_data()
