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

import calendar
import datetime
import json
import uuid
from random import choice
from random import randint
from random import uniform

from nise.generators.generator import AbstractGenerator

AZURE_COLUMNS_V2_SUBSCRIPTION = (
    "InvoiceSectionName",
    "AccountName",
    "AccountOwnerId",
    "SubscriptionId",
    "SubscriptionName",
    "ResourceGroupName",
    "ResourceLocation",
    "Date",
    "ProductName",
    "MeterCategory",
    "MeterSubCategory",
    "MeterId",
    "MeterName",
    "MeterRegion",
    "UnitOfMeasure",
    "Quantity",
    "EffectivePrice",
    "CostInBillingCurrency",
    "CostCenter",
    "ConsumedService",
    "ResourceId",
    "Tags",
    "OfferId",
    "AdditionalInfo",
    "ServiceInfo1",
    "ServiceInfo2",
    "ResourceName",
    "ReservationId",
    "ReservationName",
    "UnitPrice",
    "ProductOrderId",
    "ProductOrderName",
    "Term",
    "PublisherType",
    "PublisherName",
    "ChargeType",
    "Frequency",
    "PricingModel",
    "AvailabilityZone",
    "BillingAccountId",
    "BillingCurrency",
    "BillingAccountName",
    "BillingPeriodStartDate",
    "BillingPeriodEndDate",
    "BillingProfileId",
    "BillingProfileName",
    "InvoiceSectionId",
    "IsAzureCreditEligible",
    "PartNumber",
    "PayGPrice",
    "PlanName",
    "ServiceFamily",
    "invoiceId",
    "previousInvoiceId",
    "resellerName",
    "resellerMpnId",
    "servicePeriodEndDate",
    "servicePeriodStartDate",
    "ProductId",
    "publisherId",
    "Location",
    "pricingCurrency",
    "costInPricingCurrency",
    "costInUsd",
    "paygCostInBillingCurrency",
    "paygCostInUsd",
    "exchangeRatePricingToBilling",
    "exchangeRateDate",
)

AZURE_COLUMNS_V2_RESOURCE_GROUP = (
    "InvoiceSectionName",
    "AccountName",
    "AccountOwnerId",
    "SubscriptionGuid",
    "SubscriptionName",
    "ResourceGroup",
    "ResourceLocation",
    "Date",
    "MeterCategory",
    "MeterSubCategory",
    "MeterId",
    "MeterName",
    "MeterRegion",
    "UnitOfMeasure",
    "Quantity",
    "EffectivePrice",
    "CostInBillingCurrency",
    "CostCenter",
    "ConsumedService",
    "Tags",
    "OfferId",
    "AdditionalInfo",
    "ServiceInfo1",
    "ServiceInfo2",
    "ResourceName",
    "ReservationId",
    "ReservationName",
    "UnitPrice",
    "ProductOrderId",
    "ProductOrderName",
    "Term",
    "PublisherType",
    "PublisherName",
    "ChargeType",
    "Frequency",
    "PricingModel",
    "AvailabilityZone",
    "BillingAccountId",
    "BillingCurrencyCode",
    "BillingAccountName",
    "BillingPeriodStartDate",
    "BillingPeriodEndDate",
    "BillingProfileId",
    "BillingProfileName",
    "InstanceName",
    "InvoiceSectionId",
    "IsAzureCreditEligible",
    "PartNumber",
    "MarketPrice",
    "PlanName",
    "ServiceFamily",
    "invoiceId",
    "previousInvoiceId",
    "resellerName",
    "resellerMpnId",
    "servicePeriodEndDate",
    "servicePeriodStartDate",
    "Product",
    "ProductId",
    "publisherId",
    "Location",
    "pricingCurrencyCode",
    "costInPricingCurrency",
    "costInUsd",
    "paygCostInBillingCurrency",
    "paygCostInUsd",
    "exchangeRate",
    "exchangeRateDate",
)

DATE_FMT = "%Y-%m-%d"


class AzureGenerator(AbstractGenerator):
    """Defines an abstract class for generators."""

    SERVICE_METER = [None]
    SERVICE_INFO_2 = [None]
    EXAMPLE_RESOURCE = [None]
    ADDITIONAL_INFO = [None]

    ACCTS_STR = {
        "SQL Database": ("Microsoft.Sql", "servers"),
        "Storage": ("Microsoft.Storage", "storageAccounts"),
        "Virtual Machines": ("Microsoft.Compute", "virtualMachines"),
        "Virtual Network": ("Microsoft.Network", "publicIPAddresses"),
    }

    RESOURCE_LOCATION = (
        ("US East", "US East"),
        ("US East", "Zone 1"),
        ("US East", ""),
        ("US North Central", "US North Central"),
        ("US North Central", "Zone 1"),
        ("US North Central", ""),
        ("US South Central", "US South Central"),
        ("US South Central", "Zone 1"),
        ("US South Central", ""),
        ("US West", "US West"),
        ("US West", "Zone 1"),
        ("US West", ""),
        ("US Central", "US Central"),
        ("US Central", "Zone 1"),
        ("US Central", ""),
        ("US East 2", "US East 2"),
        ("US West 2", "US West 2"),
    )

    SERVICE_NAMES = ["SQL Database", "Storage", "Virtual Machines", "Virtual Network"]
    SERVICE_FAMILIES = ("Compute", "Storage", "Networking")

    INVOICE_SECTION_NAMES = ("IT Services",)

    @property
    def meter_id(self):
        if self._meter_id is None:
            self._meter_id = uuid.uuid4()
        return self._meter_id

    @property
    def meter_name(self):
        if self._meter_name is None:
            _, _, meter_name, _ = self._get_cached_meter_values(self.meter_id, self.SERVICE_METER)
            self._meter_name = meter_name
        return self._meter_name

    def __init__(self, start_date, end_date, currency, account_info, attributes=None):  # noqa: C901
        """Initialize the generator."""
        self.azure_columns = AZURE_COLUMNS_V2_SUBSCRIPTION
        self.subscription_guid = account_info.get("subscription_guid")
        self.account_info = account_info
        self.usage_accounts = account_info.get("usage_accounts")
        self.attributes = attributes
        self._tags = None
        self.num_instances = 1 if attributes else randint(2, 60)
        self._usage_quantity = None
        self._resource_rate = None
        self._pre_tax_cost = None
        self._instance_id = None
        self._meter_id = None
        self._meter_name = None
        self._resource_location = None
        self._service_tier = None
        self._consumed = None
        self._resource_type = None
        self._meter_cache = {}
        self._billing_currency = currency
        self._additional_info = None
        self._data_direction = None
        self._invoice_section_id = None
        self._invoice_section_name = None

        if attributes:
            for key, value in attributes.items():
                attr_name = "_" + key
                setattr(self, attr_name, value)
            if attributes.get("resource_group_export"):
                self.azure_columns = AZURE_COLUMNS_V2_RESOURCE_GROUP
        super().__init__(start_date, end_date)

    @staticmethod
    def first_day_of_month(in_date):
        return in_date.replace(day=1).date()

    @staticmethod
    def last_day_of_month(in_date):
        _, num_days = calendar.monthrange(in_date.year, in_date.month)
        return in_date.replace(day=num_days).date()

    def _get_accts_str(self, service_name):
        """Return instance idea fields."""
        if service_name == "Bandwidth":
            service_name = choice(self.SERVICE_NAMES)
        return self.ACCTS_STR[service_name]

    def _get_cached_meter_values(self, meter_id, service_meter):
        """Return meter cached meter data to ensure meter_id and values are consistent."""
        if not self._meter_cache.get(meter_id):
            self._meter_cache[meter_id] = choice(service_meter)
        return self._meter_cache.get(meter_id)

    def _get_resource_info(self, meter_id, service_meter, ex_resource, service_info):
        """Return resource information."""
        service_tier, meter_sub, meter_name, units_of_measure = self._get_cached_meter_values(meter_id, service_meter)
        service_info_2 = choice(service_info)
        resource_group, resource_name = choice(ex_resource)
        additional_info = self._get_additional_info(meter_name)
        if self._instance_id:
            self._consumed, second_part = accts_str = self._get_accts_str(self._service_name)
            self._resource_type = self._consumed + "/" + second_part
            instance_id = self._instance_id
        else:
            self._consumed, second_part = accts_str = self._get_accts_str(self._service_name)
            self._resource_type = self._consumed + "/" + second_part
            accts_str = "/providers/" + self._resource_type + "/"
            instance_id = "{}/{}/{}/{}/{}/{}".format(
                "subscriptions",
                self.subscription_guid,
                "resourceGroups",
                resource_group,
                accts_str[1:-2],
                resource_name,
            )
        return (
            resource_group,
            instance_id,
            service_tier,
            meter_sub,
            meter_name,
            units_of_measure,
            additional_info,
            service_info_2,
        )

    def _add_common_usage_info(self, row, start, end, **kwargs):
        """Not needed for Azure."""

    def _get_location_info(self):
        """Get bandwidth info."""
        azure_region, meter_region = self._get_location()
        return azure_region, meter_region

    def _pick_tag(self, key1, val1, key2, val2):
        """Generate a randomized 2-item tag or blank tag from options."""
        if self._tags:
            tags = self._tags
        elif self.attributes and self.attributes.get("tags"):
            tags = None
        else:
            init_tag = {key1: choice(val1), key2: choice(val2)}
            tag_choices = (init_tag, "")
            tags = choice(tag_choices)
        return tags

    def _init_data_row(self, start, end, **kwargs):  # noqa: C901
        """Create a row of data with placeholder for all headers."""
        if not (start and end):
            raise ValueError("start and end must be date objects.")
        if not isinstance(start, datetime.datetime):
            raise ValueError("start must be a date object.")
        if not isinstance(end, datetime.datetime):
            raise ValueError("end must be a date object.")

        row = {}
        for column in self.azure_columns:
            row[column] = ""
        return row

    def _get_location(self):
        """Pick resource location."""
        if self._resource_location:
            location = choice([option for option in self.RESOURCE_LOCATION if self._resource_location in option])
        else:
            location = choice(self.RESOURCE_LOCATION)
        return location

    def _get_additional_info(self, meter_name=None):
        """Pick additional info."""
        if self._additional_info:
            return self._additional_info
        else:
            return choice(self.ADDITIONAL_INFO)

    def _add_tag_data(self, row):
        """Add tag dictionary data options to the row."""
        if not self._tags:
            self._tags = self._pick_tag(
                "environment", ("dev", "ci", "qa", "stage", "prod"), "project", ("p1", "p2", "p3")
            )
        row["Tags"] = json.dumps(self._tags)

    def _update_data(self, row, start, end, **kwargs):
        """Update data with generator specific data."""
        meter_id = self._meter_id if self._meter_id else self.fake.uuid4()
        rate = self._resource_rate if self._resource_rate else round(uniform(0.1, 0.50), 5)
        amount = self._usage_quantity if self._usage_quantity else uniform(0.01, 1)
        cost = self._pre_tax_cost if self._pre_tax_cost else amount * rate
        azure_region, meter_region = self._get_location_info()
        (
            resource_group,
            instance_id,
            service_tier,
            meter_sub,
            meter_name,
            units_of_measure,
            additional_info,
            service_info_2,
        ) = self._get_resource_info(meter_id, self.SERVICE_METER, self.EXAMPLE_RESOURCE, self.SERVICE_INFO_2)
        if not additional_info:
            additional_info = ""
        if not service_info_2:
            service_info_2 = ""

        if self.usage_accounts:
            usage_account = choice(self.usage_accounts)
            row["AccountName"] = usage_account[0]
            row["AccountOwnerId"] = usage_account[1]
        row["SubscriptionName"] = self.account_info.get("subscription_name")
        row["BillingAccountId"] = self.account_info.get("billing_account_id")
        row["BillingAccountName"] = self.account_info.get("billing_account_name")
        row["BillingProfileId"] = self.account_info.get("billing_account_id")
        row["BillingProfileName"] = self.account_info.get("billing_account_name")
        row["Date"] = start.date().strftime(DATE_FMT)
        row["BillingPeriodStartDate"] = self.first_day_of_month(start).strftime(DATE_FMT)
        row["BillingPeriodEndDate"] = self.last_day_of_month(start).strftime(DATE_FMT)
        row["ResourceLocation"] = azure_region
        row["MeterCategory"] = self._service_name
        row["MeterId"] = str(self.meter_id)
        row["MeterName"] = self.meter_name
        row["MeterRegion"] = meter_region
        row["ConsumedService"] = self._consumed
        row["OfferId"] = ""
        row["AdditionalInfo"] = json.dumps(additional_info)
        row["ServiceInfo1"] = ""
        row["ServiceInfo2"] = service_info_2
        row["UnitOfMeasure"] = units_of_measure
        row = self._map_header_to_report_version(
            row, meter_sub, str(amount), str(rate), str(cost), instance_id, service_tier
        )

        if instance_id and "resourceGroups/" in instance_id:
            resource_group = instance_id.split("resourceGroups/")[-1].split("/")[0]

        if self.azure_columns is AZURE_COLUMNS_V2_SUBSCRIPTION:
            row["SubscriptionId"] = self.subscription_guid
            row["ResourceGroupName"] = resource_group
            row["ProductName"] = ""
            row["PayGPrice"] = 0
        else:
            row["SubscriptionGuid"] = self.subscription_guid
            row["ResourceGroup"] = resource_group
            row["MarketPrice"] = 0

        resource_name = instance_id.split("/")[-1] if instance_id else ""

        if self._service_name == "Virtual Machines":
            if getattr(self, "_CCSP", False):
                publisher_name = "Microsoft"
                service_family = "Compute"
                row["MeterCategory"] = "Virtual Machine Licenses"
            else:
                publisher_name = "Red Hat Enterprise Linux"
                service_family = choice(self.SERVICE_FAMILIES + ("Azure Marketplace Services",))
            publisher_type = "Marketplace"
        else:
            service_family = choice(self.SERVICE_FAMILIES)
            publisher_name = ""
            publisher_type = "Azure"

        row["InvoiceSectionId"] = self._invoice_section_id if self._invoice_section_id else self.fake.ean(length=8)
        row["InvoiceSectionName"] = (
            self._invoice_section_name if self._invoice_section_id else choice(self.INVOICE_SECTION_NAMES)
        )

        # NOTE: Commented out columns exist in the report, but we don't have enough
        # information to date to accurately simulate values.
        row["ResourceName"] = resource_name
        row["IsAzureCreditEligible"] = "TRUE"
        row["ServiceFamily"] = service_family
        row["Frequency"] = "UsageBased"
        row["PublisherType"] = publisher_type
        row["ChargeType"] = "Usage"
        row["PublisherName"] = publisher_name
        # row['PricingModel'] =
        # row['ReservationId'] =
        # row['ReservationName'] =
        # row['ProductOrderId'] =
        # row['ProductOrderName'] =
        # row['AvailabilityZone'] =
        # row['Term'] =
        # row['PlanName'] =
        # row['PartNumber'] =
        # row['CostCenter'] =
        # row['previousInvoiceId'] =
        # row['resellerName'] =
        # row['resellerMpnId'] =
        # row['servicePeriodEndDate'] =
        # row['servicePeriodStartDate'] =
        # row['Product'] =
        # row['ProductId'] =
        # row['publisherId'] =
        # row['Location'] =
        # row['pricingCurrencyCode'] =
        # row['costInPricingCurrency'] =
        # row['costInUsd'] =
        # row['paygCostInBillingCurrency'] =
        # row['paygCostInUsd'] =
        # row['exchangeRate'] =
        # row['exchangeRateDate'] =
        # row['offerid'] =
        # row['serviceinfo1'] =
        # row['instancename'] =
        # row['invoiceId'] =

        if hasattr(self, "_product_id"):
            row["ProductId"] = self._product_id
        self._add_tag_data(row)

        return row

    def _map_header_to_report_version(self, row, meter_sub, amount, rate, cost, instance_id, service_tier):
        row["Quantity"] = amount
        row["MeterSubCategory"] = meter_sub
        row["EffectivePrice"] = rate
        row["UnitPrice"] = rate
        row["CostInBillingCurrency"] = cost

        if self.azure_columns is AZURE_COLUMNS_V2_SUBSCRIPTION:
            row["ResourceId"] = instance_id
            row["BillingCurrency"] = self._billing_currency
        else:
            row["InstanceName"] = instance_id
            row["BillingCurrencyCode"] = self._billing_currency

        return row

    def _generate_hourly_data(self, **kwargs):
        """Create hourly data."""
        # not required for azure
        return []

    def _generate_daily_data(self):
        """Create daily data."""
        data = []
        for day in self.days:
            start = day.get("start")
            end = day.get("end")
            row = self._init_data_row(start, end)
            row = self._update_data(row, start, end)
            data.append(row)
        return data

    def generate_data(self, report_type=None):
        """Responsible for generating data."""
        return self._generate_daily_data()

    def get_meter_cache(self):
        """Return the meter cache for cross month generation."""
        return self._meter_cache
