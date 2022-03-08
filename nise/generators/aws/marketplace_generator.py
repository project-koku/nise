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
import datetime
from random import choice
from random import randint
from random import uniform

from nise.generators.aws.aws_constants import REGIONS
from nise.generators.generator import AbstractGenerator

IDENTITY_COLS = ("identity/LineItemId", "identity/TimeInterval")
BILL_COLS = (
    "bill/InvoiceId",
    "bill/BillingEntity",
    "bill/BillType",
    "bill/PayerAccountId",
    "bill/BillingPeriodStartDate",
    "bill/BillingPeriodEndDate",
)
LINE_ITEM_COLS = (
    "lineItem/UsageAccountId",
    "lineItem/LineItemType",
    "lineItem/UsageStartDate",
    "lineItem/UsageEndDate",
    "lineItem/ProductCode",
    "lineItem/UsageType",
    "lineItem/Operation",
    "lineItem/AvailabilityZone",
    "lineItem/ResourceId",
    "lineItem/UsageAmount",
    "lineItem/NormalizationFactor",
    "lineItem/NormalizedUsageAmount",
    "lineItem/CurrencyCode",
    "lineItem/UnblendedRate",
    "lineItem/UnblendedCost",
    "lineItem/BlendedRate",
    "lineItem/BlendedCost",
    "lineItem/LineItemDescription",
    "lineItem/TaxType",
    "lineItem/LegalEntity",
)
PRODUCT_COLS = (
    "product/ProductName",
    "product/availability",
    "product/availabilityZone",
    "product/capacitystatus",
    "product/classicnetworkingsupport",
    "product/clockSpeed",
    "product/currentGeneration",
    "product/databaseEngine",
    "product/dedicatedEbsThroughput",
    "product/description",
    "product/durability",
    "product/ecu",
    "product/edition",
    "product/endpointType",
    "product/engineCode",
    "product/enhancedNetworkingSupported",
    "product/fromLocation",
    "product/fromLocationType",
    "product/fromRegionCode",
    "product/group",
    "product/groupDescription",
    "product/instanceFamily",
    "product/instanceType",
    "product/instanceTypeFamily",
    "product/intelAvx2Available",
    "product/intelAvxAvailable",
    "product/intelTurboAvailable",
    "product/licenseModel",
    "product/location",
    "product/locationType",
    "product/marketoption",
    "product/maxIopsBurstPerformance",
    "product/maxIopsvolume",
    "product/maxThroughputvolume",
    "product/maxVolumeSize",
    "product/memory",
    "product/networkPerformance",
    "product/normalizationSizeFactor",
    "product/operatingSystem",
    "product/operation",
    "product/physicalProcessor",
    "product/platousagetype",
    "product/platovolumetype",
    "product/preInstalledSw",
    "product/processorArchitecture",
    "product/processorFeatures",
    "product/productFamily",
    "product/provisioned",
    "product/region",
    "product/regionCode",
    "product/routingTarget",
    "product/routingType",
    "product/servicecode",
    "product/servicename",
    "product/sku",
    "product/storage",
    "product/storageClass",
    "product/storageMedia",
    "product/subscriptionType",
    "product/tenancy",
    "product/toLocation",
    "product/toLocationType",
    "product/toRegionCode",
    "product/transferType",
    "product/usagetype",
    "product/vcpu",
    "product/version",
    "product/volumeApiName",
    "product/volumeType",
    "product/vpcnetworkingsupport",
)
PRICING_COLS = (
    "pricing/RateCode",
    "pricing/RateId",
    "pricing/currency",
    "pricing/publicOnDemandCost",
    "pricing/publicOnDemandRate",
    "pricing/term",
    "pricing/unit",
)
RESERVE_COLS = (
    "reservation/AmortizedUpfrontCostForUsage",
    "reservation/AmortizedUpfrontFeeForBillingPeriod",
    "reservation/EffectiveCost",
    "reservation/EndTime",
    "reservation/ModificationStatus",
    "reservation/NormalizedUnitsPerReservation",
    "reservation/NumberOfReservations",
    "reservation/RecurringFeeForUsage",
    "reservation/StartTime",
    "reservation/SubscriptionId",
    "reservation/TotalReservedNormalizedUnits",
    "reservation/TotalReservedUnits",
    "reservation/UnitsPerReservation",
    "reservation/UnusedAmortizedUpfrontFeeForBillingPeriod",
    "reservation/UnusedNormalizedUnitQuantity",
    "reservation/UnusedQuantity",
    "reservation/UnusedRecurringFee",
    "reservation/UpfrontValue",
)
SAVINGS_COLS = (
    "savingsPlan/TotalCommitmentToDate",
    "savingsPlan/SavingsPlanARN",
    "savingsPlan/SavingsPlanRate",
    "savingsPlan/UsedCommitment",
    "savingsPlan/SavingsPlanEffectiveCost",
    "savingsPlan/AmortizedUpfrontCommitmentForBillingPeriod",
    "savingsPlan/RecurringCommitmentForBillingPeriod",
)

LEGAL_ENTITY_CHOICES = ("Red Hat", "Red Hat Inc.", "Amazon Web Services, Inc.")


class MarketplaceGenerator(AbstractGenerator):
    """Defines a generator for AWS Marketplace"""

    RESOURCE_TAG_COLS = {"resourceTags/aws:createdBy", "resourceTags/user:insights_project"}

    AWS_COLUMNS = set(
        IDENTITY_COLS
        + BILL_COLS
        + LINE_ITEM_COLS
        + PRODUCT_COLS
        + PRICING_COLS
        + RESERVE_COLS
        + SAVINGS_COLS
        + tuple(RESOURCE_TAG_COLS)
    )

    def __init__(self, start_date, end_date, currency, payer_account, usage_accounts, attributes=None, tag_cols=None):
        super().__init__(start_date, end_date)
        """Initialize the generator."""
        self.payer_account = payer_account
        self.usage_accounts = usage_accounts
        self.attributes = attributes
        self._tags = None
        self.num_instances = 1 if attributes else randint(2, 60)
        self._amount = uniform(0.2, 6000.99)
        self._rate = round(uniform(0.02, 0.06), 3)
        self._product_sku = self.fake.pystr(min_chars=12, max_chars=12).upper()
        self._resource_id = "i-{}".format(self.fake.ean8())
        self._currency = currency
        self._legal_entity = None

        for attribute in self.attributes:
            setattr(self, f"_{attribute}", self.attributes.get(attribute))

        if tag_cols:
            self.RESOURCE_TAG_COLS.update(tag_cols)
            self.AWS_COLUMNS.update(tag_cols)

    @staticmethod
    def timestamp(in_date):
        """Provide timestamp for a date."""
        if not (in_date and isinstance(in_date, datetime.datetime)):
            raise ValueError("in_date must be a date object.")
        return in_date.strftime("%Y-%m-%dT%H:%M:%SZ")

    @staticmethod
    def time_interval(start, end):
        """Create a time interval string from input dates."""
        start_str = MarketplaceGenerator.timestamp(start)
        end_str = MarketplaceGenerator.timestamp(end)
        return str(start_str) + "/" + str(end_str)

    def _pick_tag(self, tag_key, options):
        """Generate tag from options."""
        if self._tags:
            tags = self._tags.get(tag_key)
        elif self.attributes:
            tags = None
        else:
            tags = choice(options)
        return tags

    def _init_data_row(self, start, end, **kwargs):  # noqa: C901
        """Create a row of data with placeholder for all headers."""
        if not (start and end):
            raise ValueError("start and end must be date objects.")
        if not isinstance(start, datetime.datetime):
            raise ValueError("start must be a date object.")
        if not isinstance(end, datetime.datetime):
            raise ValueError("end must be a date object.")

        bill_begin = start.replace(microsecond=0, second=0, minute=0, hour=0, day=1)
        bill_end = AbstractGenerator.next_month(bill_begin)
        row = {}
        COL_MAP = {
            "identity/LineItemId": self.fake.sha1(raw_output=False),
            "identity/TimeInterval": MarketplaceGenerator.time_interval(start, end),
            "bill/BillingEntity": "AWS",
            "bill/BillType": "Anniversary",
            "bill/PayerAccountId": self.payer_account,
            "bill/BillingPeriodStartDate": MarketplaceGenerator.timestamp(bill_begin),
            "bill/BillingPeriodEndDate": MarketplaceGenerator.timestamp(bill_end),
        }
        for column in self.AWS_COLUMNS:
            row[column] = ""
            if COL_MAP.get(column):
                row[column] = COL_MAP.get(column)

        return row

    def _get_location(self):
        """Pick instance location."""
        options = None
        if self.attributes and self.attributes.get("region"):
            region = self.attributes.get("region")
            options = [option for option in REGIONS if region in option]
        if options:
            location = choice(options)
        else:
            location = choice(REGIONS)
        return location

    def _add_common_usage_info(self, row, start, end, **kwargs):
        """Add common usage information."""
        row["lineItem/UsageAccountId"] = choice(self.usage_accounts)
        row["lineItem/LineItemType"] = "Usage"
        row["lineItem/UsageStartDate"] = start
        row["lineItem/UsageEndDate"] = end
        return row

    def _add_tag_data(self, row):
        """Add tag data to the row."""
        if self._tags:
            for tag in self._tags:
                row[tag] = self._tags[tag]
        else:
            num_tags = self.fake.random_int(0, 5)
            for _ in range(num_tags):
                seen_tags = set()
                tag_key = choice(list(self.RESOURCE_TAG_COLS))
                if tag_key not in seen_tags:
                    row[tag_key] = self.fake.word()
                    seen_tags.update([tag_key])

    def _generate_region_short_code(self, region):
        """Generate the AWS short code for a region."""
        split_region = region.split("-")
        return split_region[0][0:2].upper() + split_region[1][0].upper() + split_region[2]

    def _update_data(self, row, start, end, **kwargs):
        """Update data with generator specific data."""
        self.AWS_COLUMNS.update(self.AWS_COLUMNS)
        row = self._add_common_usage_info(row, start, end)

        rate = self._rate
        amount = self._amount
        cost = amount * rate
        location, aws_region, avail_zone, _ = self._get_location()
        description = "AWS Marketplace hourly software usage|us-east-1|m5.xlarge"
        amazon_resource_name = f"arn:aws:ec2:{avail_zone}:{self.payer_account}:instance/i-{self._resource_id}"

        row["identity/LineItemId"] = "diygn5vanaqsvysz3prxwrekztiipfu7zywyauupnpmpi4fmd5dq"
        row["identity/TimeInterval"] = "2021-11-23T17:49:15Z/2021-12-01T00:00:00Z"

        row["bill/InvoiceId"] = "2021-11-23T17:49:15Z/2021-12-01T00:00:00Z"
        row["bill/BillingEntity"] = "AWS Marketplace"
        row["bill/BillType"] = "Anniversary"
        row["bill/PayerAccountId"] = "589173575009"
        row["bill/BillingPeriodStartDate"] = "2021-11-01T00:00:00Z"
        row["bill/BillingPeriodEndDate"] = "2021-12-01T00:00:00Z"

        row["lineItem/UsageAccountId"] = choice(self.usage_accounts)
        row["lineItem/LegalEntity"] = self._legal_entity if self._legal_entity else choice(LEGAL_ENTITY_CHOICES)
        row["lineItem/LineItemType"] = "Usage"
        row["lineItem/UsageStartDate"] = start
        row["lineItem/UsageEndDate"] = end
        row["lineItem/ProductCode"] = "5hnnev4d0v7mapf09j0v8of0o2"
        row["lineItem/UsageType"] = "SoftwareUsage:m5.xlarge"
        row["lineItem/Operation"] = "Hourly"
        row["lineItem/AvailabilityZone"] = avail_zone
        row["lineItem/ResourceId"] = amazon_resource_name
        row["lineItem/UsageAmount"] = "1"
        row["lineItem/CurrencyCode"] = self._currency
        row["lineItem/UnblendedRate"] = rate
        row["lineItem/UnblendedCost"] = cost
        row["lineItem/BlendedRate"] = rate
        row["lineItem/BlendedCost"] = cost
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

    def _generate_hourly_data(self, **kwargs):
        """Create hourly data."""
        for hour in self.hours:
            start = hour.get("start")
            end = hour.get("end")
            row = self._init_data_row(start, end)
            row = self._update_data(row, start, end)
            yield row

    def generate_data(self, report_type=None):
        """Responsibile for generating data."""
        return self._generate_hourly_data()
