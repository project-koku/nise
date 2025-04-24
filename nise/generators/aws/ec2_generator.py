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

from dateutil.relativedelta import relativedelta
from nise.generators.aws.aws_generator import AWSGenerator


class EC2Generator(AWSGenerator):
    """Generator for EC2 data."""

    INSTANCE_TYPES = (
        # NOTE: Each tuple represents
        # (instance type,
        # physical_cores,
        # vCPUs,
        # memory,
        # storage,
        # family,
        # cost,
        # rate,
        # saving,
        # amount,
        # reserved_instances,
        # upfront_fee
        # recurring_fee
        # savings_negation,
        # description)
        (
            "m5.large",
            "1",
            "2",
            "8 GiB",
            "EBS Only",
            "General Purpose",
            "0.096",
            "0.096",
            "0.045",
            1,
            False,
            False,
            False,
            False,
            "${cost} per On Demand Linux {inst_type} Instance Hour",
        ),
        (
            "c5d.2xlarge",
            "4",
            "8",
            "16 GiB",
            "1 x 200 NVMe SSD",
            "Compute Optimized",
            "0.34",
            "0.34",
            "0.17",
            1,
            False,
            False,
            False,
            False,
            "${cost} per On Demand Linux {inst_type} Instance Hour",
        ),
        (
            "c4.xlarge",
            "2",
            "4",
            "7.5 GiB",
            "EBS-Only",
            "Compute Optimized",
            "0.199",
            "0.199",
            "0.099",
            1,
            False,
            False,
            False,
            False,
            "${cost} per On Demand Linux {inst_type} Instance Hour",
        ),
        (
            "r4.large",
            "1",
            "2",
            "15.25 GiB",
            "EBS-Only",
            "Memory Optimized",
            "0.133",
            "0.133",
            "0.067",
            1,
            False,
            False,
            False,
            False,
            "${cost} per On Demand Linux {inst_type} Instance Hour",
        ),
    )

    ARCHS = ("32-bit", "64-bit")

    OPERATING_SYSTEMS = (
        "Amazon Linux",
        "Ubuntu",
        "Windows Server",
        "Red Hat Enterprise Linux",
        "SUSE Linux Enterprise Server",
        "openSUSE Leap",
        "Fedora",
        "Fedora CoreOS",
        "Debian",
        "CentOS",
        "Gentoo Linux",
        "Oracle Linux",
        "FreeBSD",
    )

    def __init__(self, start_date, end_date, currency, payer_account, usage_accounts, attributes=None, tag_cols=None):
        """Initialize the EC2 generator."""
        super().__init__(start_date, end_date, currency, payer_account, usage_accounts, attributes, tag_cols)
        self._instance_type = choice(self.INSTANCE_TYPES)
        self._operating_system = self.attributes.get("operating_system", choice(self.OPERATING_SYSTEMS))
        self._processor_arch = self.attributes.get("processor_arch", choice(self.ARCHS))
        self._resource_id = f"i-{self.attributes.get('resource_id', self.fake.ean8())}"
        self._product_sku = self.attributes.get("product_sku", self.fake.pystr(min_chars=12, max_chars=12).upper())
        self._tags = self.attributes.get("tags", [])

        if instance_type := self.attributes.get("instance_type"):
            self._instance_type = (
                instance_type.get("inst_type"),
                instance_type.get("physical_cores"),
                instance_type.get("vcpu"),
                instance_type.get("memory"),
                instance_type.get("storage"),
                instance_type.get("family"),
                instance_type.get("cost"),
                instance_type.get("rate"),
                instance_type.get("saving"),
                instance_type.get("amount", "1"),
                instance_type.get("reserved_instance", False),
                instance_type.get("upfront_fee", False),
                instance_type.get("recurring_fee", False),
                instance_type.get("negation", False),
                "${cost} per On Demand Linux {inst_type} Instance Hour",
            )

    def _update_data(self, row, start, end, **kwargs):
        """Update data with generator specific data."""
        (
            inst_type,
            physical_cores,
            vcpu,
            memory,
            storage,
            family,
            cost,
            rate,
            saving,
            amount,
            reserved_instance,
            upfront_fee,
            recurring_fee,
            negation,
            description,
        ) = self._instance_type

        inst_description = description.format(cost=cost, inst_type=inst_type)
        product_name = "Amazon Elastic Compute Cloud"
        billing_entity = "AWS"
        if self.attributes:
            inst_description = self.attributes.get("lineitem_lineitemdescription", inst_description)
            product_name = self.attributes.get("product_name", product_name)
            billing_entity = self.attributes.get("billing_entity", billing_entity)
        location, aws_region, avail_zone, _ = self._get_location()
        row = self._add_common_usage_info(row, start, end)
        row["bill/BillingEntity"] = billing_entity
        row["lineItem/ProductCode"] = "AmazonEC2"
        row["lineItem/UsageType"] = f"BoxUsage:{inst_type}"
        row["lineItem/Operation"] = "RunInstances"
        row["lineItem/AvailabilityZone"] = avail_zone
        row["lineItem/ResourceId"] = self._resource_id
        row["lineItem/UsageAmount"] = amount
        row["lineItem/UnblendedRate"] = rate
        row["lineItem/UnblendedCost"] = cost
        row["lineItem/BlendedRate"] = rate
        row["lineItem/BlendedCost"] = cost
        row["lineItem/LineItemDescription"] = inst_description
        row["product/ProductName"] = product_name
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
        row["product/operatingSystem"] = self._operating_system
        row["product/operation"] = "RunInstances"
        row["product/physicalCores"] = physical_cores
        row["product/physicalProcessor"] = "Intel Xeon Family"
        row["product/preInstalledSw"] = "NA"
        row["product/processorArchitecture"] = self._processor_arch
        row["product/processorFeatures"] = "Intel AVX Intel Turbo"
        row["product/productFamily"] = "Compute Instance"
        row["product/region"] = aws_region
        row["product/servicecode"] = "AmazonEC2"
        row["product/sku"] = self._product_sku
        row["product/storage"] = storage
        row["product/tenancy"] = "Shared"
        row["product/usagetype"] = f"BoxUsage:{inst_type}"
        row["product/vcpu"] = vcpu
        row["pricing/publicOnDemandCost"] = cost
        row["pricing/publicOnDemandRate"] = rate
        row["pricing/term"] = "OnDemand"
        row["pricing/unit"] = "Hrs"
        row["savingsPlan/SavingsPlanEffectiveCost"] = saving
        row["savingsPlan/SavingsPlanRate"] = saving

        # Overwrite lineItem/LineItemType for items with applied Savings plan
        if saving is not None:
            row["lineItem/LineItemType"] = "SavingsPlanCoveredUsage"
        # Overwrite lineitem/LineItemType for RI's discount usage
        if reserved_instance:
            row["lineItem/LineItemType"] = "DiscountedUsage"
            row["lineItem/UnblendedCost"] = 0
            row["lineItem/UnblendedRate"] = 0
            row["lineItem/BlendedCost"] = 0
            row["lineItem/BlendedRate"] = 0
            row["lineItem/LineItemDescription"] = f"{inst_type} reserved instance applied"
            row["pricing/publicOnDemandCost"] = "convertible"
            row["pricing/publicOnDemandRate"] = "No Upfront"
            row["savingsPlan/SavingsPlanEffectiveCost"] = None
            row["savingsPlan/SavingsPlanRate"] = None

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

        # Overwrite lineitem/LineItemType for Savings plan upfront and recurring fees
        if recurring_fee or upfront_fee:
            if recurring_fee:
                row["lineItem/LineItemType"] = "SavingsPlanRecurringFee"
                row["lineItem/LineItemDescription"] = "3 year No Upfront Compute Savings Plan"
                row["lineItem/UsageType"] = "ComputeSP:3yrNoUpfront"

            else:  # upfront
                row["lineItem/LineItemType"] = "SavingsPlanUpfrontFee"
                row["lineItem/LineItemDescription"] = (
                    f"USD {cost} one-time fee for 1 year All Upfront Compute Savings Plan ID: 123456"
                )
                row["lineItem/UsageType"] = "ComputeSP:1yrAllUpfront"
                row["lineItem/UsageEndDate"] = start + relativedelta(years=+1)
                end_upfront = start + relativedelta(years=+1)
                row["lineItem/UsageEndDate"] = end_upfront
                row["identity/TimeInterval"] = self.time_interval(start, end_upfront)

            row["lineItem/ProductCode"] = row["product/productFamily"] = "ComputeSavingsPlans"
            row["lineItem/UsageAmount"] = 1
            row["product/ProductName"] = "Savings Plans for AWS Compute usage"
            row["product/location"] = "Any"
            row["product/region"] = "global"
            row["lineItem/AvailabilityZone"] = None
            row["lineItem/ResourceId"] = None
            row["lineItem/UnblendedRate"] = None
            row["lineItem/BlendedRate"] = None
            row["savingsPlan/SavingsPlanEffectiveCost"] = None
            row["savingsPlan/SavingsPlanRate"] = None
            row["product/operatingSystem"] = None

        return row

    def generate_data(self, report_type=None):
        """Responsibile for generating data."""
        return self._generate_hourly_data()
