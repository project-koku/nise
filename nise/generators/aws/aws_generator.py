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
"""Defines the abstract generator."""
import datetime
from abc import abstractmethod
from random import choice
from random import randint

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
    "lineItem/LegalEntity",
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
)
PRODUCT_COLS = (
    "product/ProductName",
    "product/accountAssistance",
    "product/architecturalReview",
    "product/architectureSupport",
    "product/availability",
    "product/availabilityZone",
    "product/bestPractices",
    "product/capacitystatus",
    "product/caseSeverityresponseTimes",
    "product/classicnetworkingsupport",
    "product/clockSpeed",
    "product/comments",
    "product/contentType",
    "product/currentGeneration",
    "product/customerServiceAndCommunities",
    "product/databaseEngine",
    "product/dedicatedEbsThroughput",
    "product/deploymentOption",
    "product/description",
    "product/directorySize",
    "product/directoryType",
    "product/directoryTypeDescription",
    "product/durability",
    "product/ebsOptimized",
    "product/ecu",
    "product/edition",
    "product/endpointType",
    "product/engineCode",
    "product/enhancedNetworkingSupported",
    "product/feeCode",
    "product/feeDescription",
    "product/fromLocation",
    "product/fromLocationType",
    "product/fromRegionCode",
    "product/group",
    "product/groupDescription",
    "product/includedServices",
    "product/instanceFamily",
    "product/instanceType",
    "product/instanceTypeFamily",
    "product/intelAvx2Available",
    "product/intelAvxAvailable",
    "product/intelTurboAvailable",
    "product/isshadow",
    "product/iswebsocket",
    "product/launchSupport",
    "product/licenseModel",
    "product/location",
    "product/locationType",
    "product/marketoption",
    "product/maxIopsBurstPerformance",
    "product/maxIopsvolume",
    "product/maxThroughputvolume",
    "product/maxVolumeSize",
    "product/memory",
    "product/memoryGib",
    "product/messageDeliveryFrequency",
    "product/messageDeliveryOrder",
    "product/minVolumeSize",
    "product/networkPerformance",
    "product/normalizationSizeFactor",
    "product/operatingSystem",
    "product/operation",
    "product/operationsSupport",
    "product/origin",
    "product/physicalProcessor",
    "product/platousagetype",
    "product/platovolumetype",
    "product/preInstalledSw",
    "product/proactiveGuidance",
    "product/processorArchitecture",
    "product/processorFeatures",
    "product/productFamily",
    "product/programmaticCaseManagement",
    "product/protocol",
    "product/provisioned",
    "product/queueType",
    "product/recipient",
    "product/region",
    "product/regionCode",
    "product/requestDescription",
    "product/requestType",
    "product/resourceEndpoint",
    "product/routingTarget",
    "product/routingType",
    "product/servicecode",
    "product/servicename",
    "product/sku",
    "product/softwareType",
    "product/storage",
    "product/storageClass",
    "product/storageMedia",
    "product/storageType",
    "product/subscriptionType",
    "product/technicalSupport",
    "product/tenancy",
    "product/thirdpartySoftwareSupport",
    "product/toLocation",
    "product/toLocationType",
    "product/toRegionCode",
    "product/training",
    "product/transferType",
    "product/usagetype",
    "product/vcpu",
    "product/version",
    "product/virtualInterfaceType",
    "product/volumeApiName",
    "product/volumeType",
    "product/vpcnetworkingsupport",
    "product/whoCanOpenCases",
)
PRICING_COLS = (
    "pricing/LeaseContractLength",
    "pricing/RateCode",
    "pricing/RateId",
    "pricing/currency",
    "pricing/OfferingClass" "pricing/PurchaseOption",
    "pricing/publicOnDemandCost",
    "pricing/publicOnDemandRate",
    "pricing/term",
    "pricing/unit",
)
RESERVE_COLS = (
    "reservation/AmortizedUpfrontCostForUsage",
    "reservation/AmortizedUpfrontFeeForBillingPeriod",
    "reservation/AvailabilityZone",
    "reservation/EffectiveCost",
    "reservation/EndTime",
    "reservation/ModificationStatus",
    "reservation/NormalizedUnitsPerReservation",
    "reservation/NumberOfReservations",
    "reservation/RecurringFeeForUsage",
    "reservation/ReservationARN",
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
    "savingsPlan/AmortizedUpfrontCommitmentForBillingPeriod",
    "savingsPlan/EndTime",
    "savingsPlan/InstanceTypeFamily",
    "savingsPlan/OfferingType",
    "savingsPlan/PaymentOption",
    "savingsPlan/PurchaseTerm",
    "savingsPlan/RecurringCommitmentForBillingPeriod",
    "savingsPlan/Region",
    "savingsPlan/SavingsPlanArn",
    "savingsPlan/SavingsPlanEffectiveCost",
    "savingsPlan/SavingsPlanRate",
    "savingsPlan/StartTime",
    "savingsPlan/TotalCommitmentToDate",
    "savingsPlan/UsedCommitment",
)


class AWSGenerator(AbstractGenerator):
    """Defines a abstract class for generators."""

    RESOURCE_TAG_COLS = {
        "resourceTags/user:environment",
        "resourceTags/user:app",
        "resourceTags/user:version",
        "resourceTags/user:storageclass",
        "resourceTags/user:openshift_cluster",
        "resourceTags/user:openshift_project",
        "resourceTags/user:openshift_node",
        "resourceTags/aws:createdBy",
    }
    COST_CATEGORY_COLS = {
        "costCategory/Charge type",
        "costCategory/CostCenter",
        "costCategory/OUs",
        "costCategory/Organization",
    }
    AWS_COLUMNS = set(
        IDENTITY_COLS
        + BILL_COLS
        + LINE_ITEM_COLS
        + PRODUCT_COLS
        + PRICING_COLS
        + RESERVE_COLS
        + SAVINGS_COLS
        + tuple(RESOURCE_TAG_COLS)
        + tuple(COST_CATEGORY_COLS)
    )

    def __init__(self, start_date, end_date, currency, payer_account, usage_accounts, attributes=None, tag_cols=None):
        """Initialize the generator."""
        self.payer_account = payer_account
        self.currency = currency
        self.usage_accounts = usage_accounts
        self.attributes = attributes if attributes else {}
        self._tags = None
        self._cost_category = None
        self.num_instances = 1 if attributes else randint(2, 60)
        if tag_cols:
            self.RESOURCE_TAG_COLS.update(tag_cols)
            self.AWS_COLUMNS.update(tag_cols)
        if attributes:
            if _cost_categories := attributes.get("cost_category"):
                self._cost_category = _cost_categories
                self.AWS_COLUMNS.update(_cost_categories.keys())

        super().__init__(start_date, end_date)

    @staticmethod
    def timestamp(in_date):
        """Provide timestamp for a date."""
        if not (in_date and isinstance(in_date, datetime.datetime)):
            raise ValueError("in_date must be a date object.")
        return in_date.strftime("%Y-%m-%dT%H:%M:%SZ")

    @staticmethod
    def time_interval(start, end):
        """Create a time interval string from input dates."""
        start_str = AWSGenerator.timestamp(start)
        end_str = AWSGenerator.timestamp(end)
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
            "identity/TimeInterval": AWSGenerator.time_interval(start, end),
            "bill/BillingEntity": "AWS",
            "bill/BillType": "Anniversary",
            "bill/PayerAccountId": self.payer_account,
            "bill/BillingPeriodStartDate": AWSGenerator.timestamp(bill_begin),
            "bill/BillingPeriodEndDate": AWSGenerator.timestamp(bill_end),
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
        row["lineItem/CurrencyCode"] = self.currency
        row["lineItem/LegalEntity"] = "Amazon Web Services, Inc."
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

    def _add_category_data(self, row):
        """Add category data to the row."""
        if self._cost_category:
            for category in self._cost_category.keys():
                row[category] = self._cost_category[category]
        else:
            num_category = self.fake.random_int(0, 5)
            for _ in range(num_category):
                seen_categories = set()
                category_key = choice(list(self.COST_CATEGORY_COLS))
                if category_key not in seen_categories:
                    row[category_key] = self.fake.word()
                    seen_categories.update([category_key])

    def _generate_region_short_code(self, region):
        """Generate the AWS short code for a region."""
        split_region = region.split("-")
        return split_region[0][0:2].upper() + split_region[1][0].upper() + split_region[2]

    @abstractmethod
    def _update_data(self, row, start, end, **kwargs):
        """Update data with generator specific data."""

    def _generate_hourly_data(self, **kwargs):
        """Create hourly data."""
        for hour in self.hours:
            start = hour.get("start")
            end = hour.get("end")
            row = self._init_data_row(start, end)
            row = self._update_data(row, start, end)
            yield row

    @abstractmethod
    def generate_data(self, report_type=None):
        """Responsible for generating data."""
