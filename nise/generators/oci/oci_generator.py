#
# Copyright 2022 Red Hat, Inc.
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
from random import choice
from random import uniform

from nise.generators.generator import AbstractGenerator
from nise.generators.generator import REPORT_TYPE
from nise.generators.oci.oci_constants import OCIReportConstantColumns


OCI_COST_REPORT = "cost"
OCI_USAGE_REPORT = "usage"

OCI_IDENTITY_COLUMNS = (
    "lineItem/referenceNo",
    "lineItem/tenantId",
    "lineItem/intervalUsageStart",
    "lineItem/intervalUsageEnd",
    "product/service",
)
OCI_USAGE_PRODUCT_COLS = {"product/resource"}
OCI_COMMON_PRODUCT_COLS = (
    "product/compartmentId",
    "product/compartmentName",
    "product/region",
    "product/availabilityDomain",
    "product/resourceId",
)
OCI_COST_COLUMNS = (
    "usage/billedQuantity",
    "usage/billedQuantityOverage",
    "cost/subscriptionId",
    "cost/productSku",
    "product/Description",
    "cost/unitPrice",
    "cost/unitPriceOverage",
    "cost/myCost",
    "cost/myCostOverage",
    "cost/currencyCode",
    "cost/billingUnitReadable",
    "cost/skuUnitDescription",
    "cost/overageFlag",
)
OCI_USAGE_COLUMNS = (
    "usage/consumedQuantity",
    "usage/billedQuantity",
    "usage/consumedQuantityUnits",
    "usage/consumedQuantityMeasure",
)
OCI_CORRECTION_COLUMNS = ("lineItem/isCorrection", "lineItem/backreferenceNo")
OCI_TAGS_COLUMNS = (
    "tags/Oracle-Tags.CreatedBy",
    "tags/Oracle-Tags.CreatedOn",
    "tags/Oracle-Tags.test",
    "tags/free-form-tag",
    "tags/new-tags.tarnished-tags",
    "tags/orcl-cloud.free-tier-retained",
)
OCI_ALL_COMMON_COLUMNS = OCI_IDENTITY_COLUMNS + OCI_COMMON_PRODUCT_COLS + OCI_CORRECTION_COLUMNS + OCI_TAGS_COLUMNS

OCI_REPORT_TYPE_TO_COLS = {
    OCI_COST_REPORT: (
        OCI_IDENTITY_COLUMNS + OCI_COMMON_PRODUCT_COLS + OCI_COST_COLUMNS + OCI_CORRECTION_COLUMNS + OCI_TAGS_COLUMNS
    ),
    OCI_USAGE_REPORT: (
        OCI_IDENTITY_COLUMNS
        + tuple(OCI_USAGE_PRODUCT_COLS)
        + OCI_COMMON_PRODUCT_COLS
        + OCI_USAGE_COLUMNS
        + OCI_CORRECTION_COLUMNS
        + OCI_TAGS_COLUMNS
    ),
}


class OCIGenerator(AbstractGenerator):
    """Defines a abstract class for generators."""

    def __init__(self, start_date, end_date, currency, attributes=None):
        """Initialize the generator."""
        super().__init__(start_date, end_date)
        if attributes is None or not isinstance(attributes, dict):
            attributes = {}
        self.currency = currency
        self.constants = OCIReportConstantColumns()
        self.tenant_id = attributes.get("tenant_id", self.constants.tenant_id)
        self.reference_no = self._get_reference_num()
        self.compartment_id = self.tenant_id
        self.compartment_name = attributes.get("compartment_name", self.constants.compartment_name)
        self.region_to_domain = self.constants.region_to_domain
        self.product_region = self.region_to_domain.region
        self.availability_domain = self._get_availability_domain()
        self.is_correction = choice(["true", "false"])
        self.email_domain = self.fake.free_email_domain()
        self.subscription_id = attributes.get("subscription_id", self.constants.subscription_id)
        self.cost_overage_flag = choice(["N", "", "Y"])
        self.cost_product_sku = f"B{self.fake.random_number(fix_len=True, digits=5)}"
        self.tags = attributes.get("tags", None)
        self.usage_consumed_quantity = attributes.get("consumed_quantity", round(uniform(1000, 3000)))
        self.unit_price = attributes.get("unit_price", round(uniform(0.01, 0.09), 3))
        self.cost = self.unit_price * self.usage_consumed_quantity

    @staticmethod
    def timestamp(in_date):
        """Provide timestamp for a date."""
        if not isinstance(in_date, datetime.datetime):
            raise ValueError("in_date must be a date object.")
        return in_date.strftime("%Y-%m-%dT%H:%MZ")

    def _init_data_row(self, start, end, **kwargs):
        """Create a row of data with placeholder for all headers."""
        if not (start and end):
            raise ValueError("start and end must be date objects.")
        if not isinstance(start, datetime.datetime):
            raise ValueError("start must be a date object.")
        if not isinstance(end, datetime.datetime):
            raise ValueError("end must be a date object.")

        report_type = kwargs.get(REPORT_TYPE)
        row = {}
        for column in OCI_REPORT_TYPE_TO_COLS[report_type]:
            row[column] = ""
        return row

    def _add_common_usage_info(self, row, start, end):
        """Add common usage information."""
        data = self._get_common_usage_data(start, end)
        for column in OCI_ALL_COMMON_COLUMNS:
            row[column] = data[column]
        return row

    def _get_common_usage_data(self, start, end):
        """Generate data for common columns."""

        data = {
            "lineItem/referenceNo": f"{self.reference_no}+{self.fake.pystr(min_chars=10, max_chars=15)}==",
            "lineItem/tenantId": self.tenant_id,
            "lineItem/intervalUsageStart": OCIGenerator.timestamp(start),
            "lineItem/intervalUsageEnd": OCIGenerator.timestamp(end),
            "product/service": "",
            "product/compartmentId": self.compartment_id,
            "product/compartmentName": self.compartment_name,
            "product/region": self.product_region,
            "product/availabilityDomain": self.availability_domain,
            "product/resourceId": "",
            "lineItem/isCorrection": self.is_correction,
            "lineItem/backreferenceNo": f"{self.reference_no}+{self.fake.pystr(min_chars=10, max_chars=15)}=="
            if self.is_correction == "true"
            else "",
            "tags/Oracle-Tags.CreatedBy": f"default/{self.compartment_name}@{self.email_domain}",
            "tags/Oracle-Tags.CreatedOn": choice([self._tag_timestamp(start), self._tag_timestamp(end), ""]),
            "tags/Oracle-Tags.test": choice([self.fake.word(), ""]),
            "tags/free-form-tag": choice([self.fake.word(), ""]),
            "tags/new-tags.tarnished-tags": choice([self.fake.word(), ""]),
            "tags/orcl-cloud.free-tier-retained": choice(["true", ""]),
        }

        if self.tags:
            for key, value in self.tags.items():
                data[key] = value
        return data

    def _get_reference_num(self):
        """Get reference number"""
        ref_num = f"V2.{self.fake.pystr(min_chars=10, max_chars=15)}"
        return ref_num

    def _tag_timestamp(self, in_date):
        """Provide timestamp a tag date."""
        tag_date = ""
        if isinstance(in_date, datetime.datetime):
            tag_date = in_date.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        return tag_date

    def _get_availability_domain(self):
        """Get availability domain of the region"""
        available_domain = (
            f"{self.fake.pystr(max_chars=4)}:{self.product_region.upper()}-AD-{self.region_to_domain.domain}"
        )
        return available_domain

    def _add_cost_data(self, row, start, end, **kwargs):
        """Add cost information."""
        _data = self._get_cost_data(**kwargs)
        for column in OCI_COST_COLUMNS:
            row[column] = _data[column]
        return row

    def _get_cost_data(self, **kwargs):
        """Get cost data"""
        _cost_data = {
            "usage/billedQuantity": self.usage_consumed_quantity,
            "usage/billedQuantityOverage": choice(["", round(uniform(0.0001, 0.005), 10)]),
            "cost/subscriptionId": self.subscription_id,
            "cost/productSku": self.cost_product_sku,
            "product/Description": self.cost_product_description,
            "cost/unitPrice": self.unit_price,
            "cost/unitPriceOverage": self.unit_price,
            "cost/myCost": self.cost,
            "cost/myCostOverage": self.cost,
            "cost/currencyCode": self.currency,
            "cost/billingUnitReadable": self.cost_billing_unit,
            "cost/skuUnitDescription": self.cost_sku_unit_description,
            "cost/overageFlag": self.cost_overage_flag,
        }
        return _cost_data

    def _add_usage_data(self, row, start, end, **kwargs):
        """Add usage information."""
        row["product/resource"] = self.usage_product_resource
        _data = self._get_usage_data(**kwargs)
        for column in OCI_USAGE_COLUMNS:
            row[column] = _data[column]
        return row

    def _get_usage_data(self, **kwargs):
        """Get usage data."""
        _usage_data = {
            "usage/consumedQuantity": self.usage_consumed_quantity,
            "usage/billedQuantity": self.usage_consumed_quantity,
            "usage/consumedQuantityUnits": self.usage_consumed_quant_units,
            "usage/consumedQuantityMeasure": self.usage_consumed_quant_measure,
        }
        return _usage_data

    def _update_data(self, row, start, end, **kwargs):
        """Update a data row with compute values."""
        row["product/service"] = self.service_name
        row["product/resourceId"] = self.resource_id
        report_type = kwargs.get(REPORT_TYPE)

        if report_type == OCI_COST_REPORT:
            row = self._add_cost_data(row, start, end, **kwargs)
        if report_type == OCI_USAGE_REPORT:
            row = self._add_usage_data(row, start, end, **kwargs)
        return row

    def _generate_hourly_data(self, **kwargs):
        """Create hourly data."""
        data = {OCI_COST_REPORT: [], OCI_USAGE_REPORT: []}
        for hour in self.hours:
            start = hour.get("start")
            end = hour.get("end")
            for report_type in data:
                kwargs.update({"report_type": report_type})
                row = self._init_data_row(start, end, **kwargs)
                row = self._add_common_usage_info(row, start, end)
                row = self._update_data(row, start, end, **kwargs)
                data[report_type].append(row)
        return data

    def generate_data(self, **kwargs):
        """Generate OCI data."""
        return self._generate_hourly_data(**kwargs)
