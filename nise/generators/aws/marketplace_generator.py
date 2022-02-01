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
"""Module for s3 data generation."""
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
        row["lineItem/NormalizationFactor"] = ""
        row["lineItem/NormalizedUsageAmount"] = ""
        row["lineItem/CurrencyCode"] = "USD"
        row["lineItem/UnblendedRate"] = str(rate)
        row["lineItem/UnblendedCost"] = str(cost)
        row["lineItem/BlendedRate"] = str(rate)
        row["lineItem/BlendedCost"] = str(cost)
        row["lineItem/LineItemDescription"] = description
        row["lineItem/TaxType"] = ""
        row["lineItem/LegalEntity"] = ""

        row["product/ProductName"] = "Red Hat OpenShift Service on AWS"
        row["product/availability"] = ""
        row["product/availabilityZone"] = ""
        row["product/capacitystatus"] = ""
        row["product/classicnetworkingsupport"] = ""
        row["product/clockSpeed"] = ""
        row["product/currentGeneration"] = ""
        row["product/databaseEngine"] = ""
        row["product/dedicatedEbsThroughput"] = ""
        row["product/description"] = ""
        row["product/durability"] = ""
        row["product/ecu"] = ""
        row["product/edition"] = ""
        row["product/endpointType"] = ""
        row["product/engineCode"] = ""
        row["product/enhancedNetworkingSupported"] = ""
        row["product/fromLocation"] = ""
        row["product/fromLocationType"] = ""
        row["product/fromRegionCode"] = ""
        row["product/group"] = ""
        row["product/groupDescription"] = ""
        row["product/instanceFamily"] = ""
        row["product/instanceType"] = ""
        row["product/instanceTypeFamily"] = ""
        row["product/intelAvx2Available"] = ""
        row["product/intelAvxAvailable"] = ""
        row["product/intelTurboAvailable"] = ""
        row["product/licenseModel"] = ""
        row["product/location"] = ""
        row["product/locationType"] = ""
        row["product/marketoption"] = ""
        row["product/maxIopsBurstPerformance"] = ""
        row["product/maxIopsvolume"] = ""
        row["product/maxThroughputvolume"] = ""
        row["product/maxVolumeSize"] = ""
        row["product/memory"] = ""
        row["product/networkPerformance"] = ""
        row["product/normalizationSizeFactor"] = ""
        row["product/operatingSystem"] = ""
        row["product/operation"] = ""
        row["product/physicalProcessor"] = ""
        row["product/platousagetype"] = ""
        row["product/platovolumetype"] = ""
        row["product/preInstalledSw"] = ""
        row["product/processorArchitecture"] = ""
        row["product/processorFeatures"] = ""
        row["product/productFamily"] = ""
        row["product/provisioned"] = ""
        row["product/region"] = aws_region
        row["product/regionCode"] = ""
        row["product/routingTarget"] = ""
        row["product/routingType"] = ""
        row["product/servicecode"] = ""
        row["product/servicename"] = ""
        row["product/sku"] = self._product_sku
        row["product/storage"] = ""
        row["product/storageClass"] = ""
        row["product/storageMedia"] = ""
        row["product/subscriptionType"] = ""
        row["product/tenancy"] = ""
        row["product/toLocation"] = ""
        row["product/toLocationType"] = ""
        row["product/toRegionCode"] = ""
        row["product/transferType"] = ""
        row["product/usagetype"] = ""
        row["product/vcpu"] = ""
        row["product/version"] = ""
        row["product/volumeApiName"] = ""
        row["product/volumeType"] = ""
        row["product/vpcnetworkingsupport"] = ""

        row["pricing/RateCode"] = "VDHYUHU8G2Z5AZY3.4799GE89SK.6YS6EN2CT7"
        row["pricing/RateId"] = "4981658079"
        row["pricing/currency"] = "USD"
        row["pricing/publicOnDemandCost"] = "0"
        row["pricing/publicOnDemandRate"] = ""
        row["pricing/term"] = "OnDemand"
        row["pricing/unit"] = "Hrs"

        row["reservation/AmortizedUpfrontCostForUsage"] = ""
        row["reservation/AmortizedUpfrontFeeForBillingPeriod"] = ""
        row["reservation/EffectiveCost"] = ""
        row["reservation/EndTime"] = ""
        row["reservation/ModificationStatus"] = ""
        row["reservation/NormalizedUnitsPerReservation"] = ""
        row["reservation/NumberOfReservations"] = ""
        row["reservation/RecurringFeeForUsage"] = ""
        row["reservation/StartTime"] = ""
        row["reservation/SubscriptionId"] = "7592738291"
        row["reservation/TotalReservedNormalizedUnits"] = ""
        row["reservation/TotalReservedUnits"] = ""
        row["reservation/UnitsPerReservation"] = ""
        row["reservation/UnusedAmortizedUpfrontFeeForBillingPeriod"] = ""
        row["reservation/UnusedNormalizedUnitQuantity"] = ""
        row["reservation/UnusedQuantity"] = ""
        row["reservation/UnusedRecurringFee"] = ""
        row["reservation/UpfrontValue"] = ""

        row["savingsPlan/TotalCommitmentToDate"] = ""
        row["savingsPlan/SavingsPlanARN"] = ""
        row["savingsPlan/SavingsPlanRate"] = ""
        row["savingsPlan/UsedCommitment"] = ""
        row["savingsPlan/SavingsPlanEffectiveCost"] = ""
        row["savingsPlan/AmortizedUpfrontCommitmentForBillingPeriod"] = ""
        row["savingsPlan/RecurringCommitmentForBillingPeriod"] = ""

        row["resourceTags/aws: createdBy"] = "AssumedRole:AROAYSLL3JVQ6DYUNKWQJ:1637692740557658269"
        row["resourceTags/user: insights_project"] = ""

        self._add_tag_data(row)

        return row

    def generate_data(self, report_type=None):
        """Responsibile for generating data."""
        return self._generate_hourly_data()
